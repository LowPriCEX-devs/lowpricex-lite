# encoding:utf-8
from haystack import indexes
from lowpricex_app.models import JuegoDetalles


class JuegoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    detalles = indexes.EdgeNgramField(model_attr='detalle')
    sku = indexes.CharField()

    def get_model(self):
        return JuegoDetalles
    
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
    
    def prepare_detalles(self, obj):
        return obj.detalle
    
    def prepare_sku(self, obj):
        return str(obj.juego.sku)