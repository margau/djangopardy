from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Cardset, GameRound, Player, AnswerQuestion, AnswerQuestionAsked, Category
from django.db.models import Count
import random

# Create your views here.

def overview(request):
    cardsets = Cardset.objects.all().values()
    template = loader.get_template('overview.html')
    context = {
        'cardsets': cardsets,
    }
    return HttpResponse(template.render(context, request))

def cardset(request, id):
    cardset = Cardset.objects.get(id=id)
    if request.method == "POST":
        data = request.POST
        name = data.get("name")
        if name:
            new_round = GameRound(name=name, cardset=cardset)
            new_round.save()
    gamerounds = GameRound.objects.filter(cardset_id=id).values() 
    # question list per cardset
    points = cardset.point_steps.all().order_by('points').values()
    categories = cardset.category_set.all().values()
    answer_count = []
    # build aq list. This includes one row per category with the name, number of answers, and aggregation
    for c in categories:
        c_answer_count = []
        unasked = []
        for p in points:
            total_aqs = AnswerQuestion.objects.filter(category=c['id'], points=p['id']).count()
            c_answer_count.append(total_aqs)
            unasked_aqs = AnswerQuestion.objects.filter(category=c['id'], points=p['id'], num_asked=0).count()
            unasked.append(unasked_aqs)

        answer_count.append([c["name"]]+c_answer_count+[min(c_answer_count), min(unasked)])

    template = loader.get_template('cardset.html')
    context = {
        'cardset': cardset,
        'gamerounds': gamerounds,
        'points': points,
        'categories': categories,
        'answer_count': answer_count,
    }
    return HttpResponse(template.render(context, request))

def gameround(request, id):
    gameround = GameRound.objects.get(id=id)
    if request.method == "POST":
        data = request.POST
        name = data.get("name")
        if name:
            new_player = Player(name=name, gameround=gameround)
            new_player.save()

    players = gameround.player_set.all().values()
    template = loader.get_template('gameround.html')
    context = {
        'gameround': gameround,
        'players': players,
    }
    return HttpResponse(template.render(context, request))

def play(request, id):
    gameround = GameRound.objects.get(id=id)
    #if request.method == "POST":
    #    data = request.POST
    #    name = data.get("name")
    #    if name:
    #        new_player = Player(name=name, gameround=gameround)
    #        new_player.save()
    
    points = gameround.cardset.point_steps.all().order_by('points').values()
    players = gameround.player_set.all()
    categories = gameround.category.all().values()
    aq = []
    # build aq list
    for c in categories:
        caq = [{"cat": c["name"]}]
        for p in points: 
            aq_obj = {"aq": None, "asked": False, "player_correct":None}
            # first: was there already a question asked for that category, points and round - if yes, return this
            asked = AnswerQuestionAsked.objects.filter(gameround=gameround, answer_question__category=c['id'], answer_question__points=p['id']).first()
            if asked:
                # if we have an answer noted for this round, category and points, we can use this
                aq_obj["aq"] = asked.answer_question
                aq_obj["asked"] = True
                aq_obj["player_correct"] = asked.player_correct
            else:
                # get best new question
                aq_obj['aq']=AnswerQuestion.objects.get_best_aq(c['id'],p['id']) 
            caq.append(aq_obj)
        aq.append(caq)

    # define next player
    # get latest updated AQasked for this round
    latest_asked = AnswerQuestionAsked.objects.filter(gameround=gameround).order_by('-time_updated').first()
    next_player = None
    next_player_random = True
    if latest_asked:
        if latest_asked.player_correct:
            # get next player
            next_player = latest_asked.player_correct
            # check if this player is already asked
            next_player_random = False
    
    if next_player_random:
        # get random player
        next_player = gameround.player_set.order_by('?').first()

    template = loader.get_template('play.html')
    context = {
        'gameround': gameround,
        'players': players,
        'categories': categories,
        'points': points,
        'aq': aq,
        'next_player': next_player,
        'next_player_random': next_player_random,
    }
    return HttpResponse(template.render(context, request))

def answer(request, gameround_id, answer_id, action = "none"):
    gameround = GameRound.objects.get(id=gameround_id)
    answer = AnswerQuestion.objects.get(id=answer_id)
    players = gameround.player_set.all()
    # note that we have asked this question
    asked, newly_asked = answer.answerquestionasked_set.get_or_create(gameround=gameround)

    double = False
    double_points_min = int(answer.points.points / 2)
    double_points_max = int(answer.points.points * 2)
    # if the question was newly asked, decide if we have a double
    if newly_asked:
        if gameround.double_frequency > 0:
            if (random.random()*100) < gameround.double_frequency:
                asked.double_player = Player.objects.get(id=request.GET.get('player', None))

    # if we already have set a double player, it is of course still a double
    if asked.double_player:
        double = True
        # check if we already have points for the double player?
        if request.method == "POST":
            data = request.POST
            double_points = int(data.get("double_points"))
            if double_points and double_points >= double_points_min and double_points <= double_points_max:
                asked.double_points = double_points

    player_wrong = None
    if action == "wrong":
        pid = request.GET.get('player', None)
        player_wrong = Player.objects.get(id=pid)
        asked.player_wrong.add(player_wrong)
        # reset player correct in case thats the same
        if asked.player_correct == player_wrong:
            asked.player_correct = None

    asked.save()
    template = loader.get_template('answer.html')
    context = {
        'gameround': gameround,
        'answer': answer,
        'players': players,
        'asked': asked,
        'player_wrong': player_wrong,
        'double': double,
        'double_player': asked.double_player,
        'double_points': asked.double_points,
        'double_points_min': double_points_min,
        'double_points_max': double_points_max,
    }
    return HttpResponse(template.render(context, request))

def question(request, gameround_id, answer_id, action = "none"):
    gameround = GameRound.objects.get(id=gameround_id)
    answer = AnswerQuestion.objects.get(id=answer_id)
    players = gameround.player_set.all()
    # note that we have asked this question
    asked, _ = answer.answerquestionasked_set.get_or_create(gameround=gameround)
    player_correct = None
    player_wrong = None
    points = answer.points
    # wenn es ein double war, punkte überschreiben
    if asked.double_player:
        points = asked.double_points if asked.double_points else points.points
    # wenn es richtig war, punkte draufrechnen
    if action == "correct":
        pid = request.GET.get('player', None)
        player_correct = Player.objects.get(id=pid)
        asked.player_correct = player_correct
        # wenns richtig ist, kann es nicht falsch sein
        asked.player_wrong.remove(player_correct)
    if action == "wrong":
        pid = request.GET.get('player', None)
        player_wrong = Player.objects.get(id=pid)
        asked.player_wrong.add(player_wrong)
        # reset player correct in case thats the same
        if asked.player_correct == player_wrong:
            asked.player_correct = None    
    if action == "none":
        asked.player_correct = None
    asked.save()
    template = loader.get_template('question.html')
    context = {
        'gameround': gameround,
        'answer': answer,
        'players': players,
        'asked': asked,
        'player_correct': player_correct,
        'player_wrong': player_wrong,
        'points': points,
    }
    return HttpResponse(template.render(context, request))
