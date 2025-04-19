from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Cardset, GameRound, Player, AnswerQuestion, AnswerQuestionAsked, Category

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
    # build aq list
    for c in categories:
        c_answer_count = []
        for p in points:
            c_answer_count.append(AnswerQuestion.objects.filter(category=c['id'], points=p['id']).count())
        answer_count.append([c["name"]]+c_answer_count+[min(c_answer_count)])

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
            # first: was there already a question asked for that category, points and round - if yes, return this
            # TODO
            # get all answer questions for this category 
            aq_tmp = AnswerQuestion.objects.get_best_aq(c['id'],p['id'])
            aq_obj = {"aq": aq_tmp, "asked": False, "player_correct":None}
            # check if this question was already asked in this round
            if aq_tmp:
                asked = aq_obj["aq"].answerquestionasked_set.filter(gameround=gameround).first()
                if asked:
                    aq_obj["asked"] = True
                    aq_obj["player_correct"] = asked.player_correct
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
    asked, _ = answer.answerquestionasked_set.get_or_create(gameround=gameround)

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
    }
    return HttpResponse(template.render(context, request))

def question(request, gameround_id, answer_id, action = "none"):
    gameround = GameRound.objects.get(id=gameround_id)
    answer = AnswerQuestion.objects.get(id=answer_id)
    players = gameround.player_set.all()
    # note that we have asked this question
    asked, _ = answer.answerquestionasked_set.get_or_create(gameround=gameround)
    player_correct = None
    # wenn es richtig war, punkte draufrechnen
    if action == "correct":
        pid = request.GET.get('player', None)
        player_correct = Player.objects.get(id=pid)
        asked.player_correct = player_correct
        # wenns richtig ist, kann es nicht falsch sein
        asked.player_wrong.remove(player_correct)
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
    }
    return HttpResponse(template.render(context, request))
