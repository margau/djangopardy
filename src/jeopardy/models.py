from django.db import models
from django.db.models import Count
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

# Punkteklasse
class Points(models.Model):
    points = models.IntegerField()
        
    def __str__(self):
        return str(self.points)

# Kartensatz z.B. zu einem Thema
class Cardset(models.Model):
    name = models.CharField(max_length=50, unique=True)
    point_steps = models.ManyToManyField(Points, related_name='point_steps_cardset')

    def __str__(self):
        return self.name

# eine Kategorie in einem Kartensatz
class Category(models.Model):
    name = models.CharField(max_length=50)
    cardset = models.ForeignKey(Cardset, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# Eine Antwort mit der dazugehörigen Frage
class AnswerQuestionManager(models.Manager):
    def get_queryset(self):
        """Overrides the models.Manager method"""
        qs = super(AnswerQuestionManager, self).get_queryset().annotate(num_asked=Count('answerquestionasked'))
        return qs

    def get_best_aq(self, category, points):
        # first: get all AQs that were not answered ever in randomized order
        aq = self.filter(category=category, points=points).filter(num_asked=0).order_by('?').first()    
        if aq:
            return aq
        # if we have no answer, get the one with the oldest answer
        ret = None
        latest = None
        answers = self.filter(category=category, points=points).all()
        for a in answers:
            l = a.answerquestionasked_set.order_by('-time_asked').first()
            if latest is None:
                ret = a
                latest = l.time_asked
            # update the preferred question, if it last asked time is older than the current one
            if l.time_asked < latest:
                latest = l.time_asked
                ret = a
        return ret

class AnswerQuestion(models.Model):
    MEDIA_NONE = 'N'
    MEDIA_IMAGE = 'I'
    MEDIA_AUDIO = 'A'
    MEDIA_VIDEO = 'V'

    MEDIA_CHOICES = [
        (MEDIA_NONE, 'None'),
        (MEDIA_IMAGE, 'Image'),
        (MEDIA_AUDIO, 'Audio'),
        (MEDIA_VIDEO, 'Video')
    ]


    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    points = models.ForeignKey(Points, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=1000, blank=True)
    answer_media = models.FileField(upload_to="answer/", blank=True)
    answer_media_type = models.CharField(max_length=1, choices=MEDIA_CHOICES, default=MEDIA_NONE)
    question_text = models.CharField(max_length=1000, blank=True)
    question_media = models.FileField(upload_to="question/", blank=True)
    question_media_type = models.CharField(max_length=1, choices=MEDIA_CHOICES, default=MEDIA_NONE)
    internal_notes = models.TextField(blank=True)
    attribution = models.TextField(blank=True)

    objects = AnswerQuestionManager()

    def __str__(self):
        return self.answer_text + " - " + str(self.category) + " - " + str(self.points)

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
# Eine gespielte oder zu spielende Runde
class GameRound(models.Model):
    name = models.CharField(max_length=50)
    cardset = models.ForeignKey(Cardset, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, related_name='categories')
    double_frequency = models.DecimalField(max_digits=3, decimal_places=0, default=Decimal(0), validators=PERCENTAGE_VALIDATOR)

    def __str__(self):
        return self.name + " - " + str(self.start_time)

# ein Spieler in einer Runde
class Player(models.Model):
    name = models.CharField(max_length=50)
    gameround = models.ForeignKey(GameRound, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def points(self):
        p = 0
        # first, get correct answers
        correct = AnswerQuestionAsked.objects.filter(player_correct=self)
        for c in correct:
            # check if this was a double
            if c.double_player == self:
                p += c.double_points
            else:
                # otherwise, just add the points
                p += c.answer_question.points.points
        # then, subtract wrong answers
        wrong = AnswerQuestionAsked.objects.filter(player_wrong=self)
        for w in wrong:
            # check if this was a double
            if w.double_player == self:
                # if it was a double, we have to subtract the double points
                p -= w.double_points
            else:
                # otherwise, just subtract the points of the question
                p -= w.answer_question.points.points
        return p

# AnswerQuestionAsked ist eine Antwort, die in einer Runde gefragt wurde
class AnswerQuestionAsked(models.Model):
    answer_question = models.ForeignKey(AnswerQuestion, on_delete=models.CASCADE)
    time_asked = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)
    gameround = models.ForeignKey(GameRound, on_delete=models.CASCADE)
    player_correct = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='right_answer', blank=True)
    player_wrong = models.ManyToManyField(Player, related_name='wrong_answers', blank=True)
    double_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='double_player')
    double_points = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.answer_question) + " - " + str(self.time_asked) + " - " + str(self.gameround)


    class Meta:
        unique_together = ('answer_question', 'gameround')

