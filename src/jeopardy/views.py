from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Cardset, GameRound, Player, AnswerQuestion

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
    template = loader.get_template('cardset.html')
    context = {
        'cardset': cardset,
        'gamerounds': gamerounds,
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
    players = gameround.player_set.all().values()
    categories = gameround.category.all().values()
    aq = []
    # build aq list
    for c in categories:
        caq = []
        for p in points:   
            # get all answer questions for this category 
            caq.append(AnswerQuestion.objects.get_best_aq(c['id'],p['id']))
        aq.append(caq)
            
    template = loader.get_template('play.html')
    context = {
        'gameround': gameround,
        'players': players,
        'categories': categories,
        'points': points,
        'aq': aq,
    }
    return HttpResponse(template.render(context, request))
