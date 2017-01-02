#encoding:utf-8

from musicrecommender_app.models import Artista, UsuarioArtista, UsuarioEtiquetaArtista, Etiqueta, UsuarioAmigo
from musicrecommender_app.forms import  UsuarioBusquedaForm, UsuarioRecomendacionForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Count
from operator import itemgetter

def mostrar_mas_escuchados(request):
    artistas_top = UsuarioArtista.objects.values("idArtista").annotate(repr=Count("id")).order_by("-repr")[:3]
    top = [{"reproducciones": row["repr"], "artista": Artista.objects.filter(idArtista=row["idArtista"]).get()} for row in artistas_top]
    return render_to_response('mas_escuchados.html', {"top": top}, context_instance=RequestContext(request))

def recomendar_musica(request):
    formulario = UsuarioRecomendacionForm()
    artistasRecomendados = None
    etiquetas=None
    
    if request.method=='POST':
        formulario = UsuarioRecomendacionForm(request.POST)

        if formulario.is_valid():
            idUsuario = formulario.cleaned_data['idUsuario']
            
            #Obtenemos los grupos que más escucha y, con ellos, sus tags
            artists = UsuarioArtista.objects.filter(idUsuario=idUsuario).order_by('-tiempoEscucha')[:4]
            
            #Etiquetas de los grupos más escuchados por él y sus amigos
            amigos = UsuarioAmigo.objects.filter(idUsuario=idUsuario).values_list('idAmigo', flat=True)
            artistasAmigos = [artists]
            for amigo in amigos:
                print(amigo)
                artistasAmigos.append(UsuarioArtista.objects.filter(idUsuario=amigo).order_by('-tiempoEscucha')[:4])
                
            etiquetasPos = []
            #Obtenemos las 4 etiquetas más repetidas entre todos
            for artista in artistasAmigos:
                try:
                    tag = UsuarioEtiquetaArtista.objects.filter(idArtista = artista).annotate(num_tags=Count('idTag')).order_by('-num_tags')[:1].get()
                except:
                    continue
                etiquetasPos.append({'etiqueta':tag.idTag, 'num_tags':tag.num_tags})
                
            etiquetasPos = sorted(etiquetasPos, key=itemgetter('num_tags'), reverse=True)[:4]
            etiquetas= []
            for etiqueta in etiquetasPos:
                etiquetas.append(etiqueta['etiqueta'])
                

            idArtistas = UsuarioEtiquetaArtista.objects.filter(idTag__in=etiquetas).values_list('idArtista', flat=True)
            artistas = Artista.objects.filter(pk__in=idArtistas)
            
            idArtistas = UsuarioArtista.objects.filter(idUsuario=idUsuario).values_list('idArtista', flat=True)
            artistasEscuchados = Artista.objects.filter(pk__in=set(idArtistas))
            
            i=1
            for etiqueta in etiquetasPos:
                etiqueta['num_tags'] = i
                i = i+1
            

            artistasFinales=[]
            for artista in artistas:
                if artista not in artistasEscuchados:
                    artistasFinales.append(artista)
                    

            artistasRecomendados = []
            for artist in artistasFinales:
                idTags = UsuarioEtiquetaArtista.objects.filter(idArtista = artist).values_list('idTag', flat=True).annotate(num_tags=Count('idTag')).order_by('-num_tags')[:4]
                tags = Etiqueta.objects.filter(pk__in=set(idTags))

                fitness = 0.0
                for tag in tags:
                    i=1
                    if tag in etiquetas:
                        for etiquetaPos in etiquetasPos:
                            if tag == etiquetaPos['etiqueta']:
                                fitness = fitness + float((len(etiquetas)-i+1))/float((abs(etiquetaPos['num_tags']-i)+1))
                                    
                if fitness!= 0.0:
                    artistasRecomendados.append({'artista':artist, 'fitness':fitness, 'tags':tags})
            
            artistasRecomendados = sorted(artistasRecomendados, key=itemgetter('fitness'), reverse=True)[:2]
                            
                    
    return render_to_response('recomendar_musica.html', {'formulario':formulario, 'musica':artistasRecomendados, 'etiquetas':etiquetas}, context_instance=RequestContext(request))


def mostrar_puntuaciones_usuario(request):
    formulario = UsuarioBusquedaForm()
    musicaEscuchada = None
    
    if request.method=='POST':
        formulario = UsuarioBusquedaForm(request.POST)
        
        if formulario.is_valid():
            musicaEscuchada = UsuarioArtista.objects.filter(idUsuario=formulario.cleaned_data['idUsuario'])
            for userArtista in musicaEscuchada:
                duracion = userArtista.tiempoEscucha
                dias = duracion // 86400
                horas = (duracion % 86400) // 3600
                minutos = (duracion - horas * 3600) // 60
                segundos = (duracion - horas*3600 - minutos*60)
                userArtista.tiempoEscucha = ("%d días " % dias if dias > 0 else "") + ("%d horas " % horas if horas > 0 else "") + ("%d minutos " % minutos if minutos > 0 else "") + ("%d segundos " % segundos)
            
    return render_to_response('puntuaciones_usuario.html', {'formulario':formulario, 'musicaEscuchada':musicaEscuchada}, context_instance=RequestContext(request))

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))