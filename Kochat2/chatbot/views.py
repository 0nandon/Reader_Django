from django.shortcuts import render
from django.views.generic import TemplateView, View

from kochat.data.dataset import Dataset
from kochat.loss import CRFLoss, CenterLoss
from kochat.model import intent, embed, entity
from kochat.proc import DistanceClassifier, GensimEmbedder, EntityRecognizer
from chatbot.scenario import dust, weather, travel, restaurant, bestseller

from kochat.app.scenario_manager import ScenarioManager
from django.core.cache import cache
from django.http.response import JsonResponse


dataset = Dataset(ood=True)

emb = GensimEmbedder(model=embed.Word2Vec())

clf = DistanceClassifier(
    model=intent.CNN(dataset.intent_dict),
    loss=CenterLoss(dataset.intent_dict),
)

rcn = EntityRecognizer(
    model=entity.LSTM(dataset.entity_dict),
    loss=CRFLoss(dataset.entity_dict)
)


# 모델 학습
def fit(request):
    embed_processor = (emb, True)
    intent_classifier = (clf, True)
    entity_recognizer = (rcn, True)

    embed_processor = embed_processor[0] if isinstance(embed_processor, tuple) else embed_processor

    intent_classifier = intent_classifier[0] if isinstance(intent_classifier, tuple) else intent_classifier

    entity_recognizer = entity_recognizer[0] if isinstance(entity_recognizer, tuple) else entity_recognizer

    embed_processor.fit(dataset.load_embed())
    intent_classifier.fit(dataset.load_intent(embed_processor))
    entity_recognizer.fit(dataset.load_entity(embed_processor))
    print("done")

    return render(request, 'chatbot/test.html', {})


def return_scenario():
    scenarios = [weather, dust, travel, restaurant, bestseller]
    scenario_manager = ScenarioManager()

    for scenario in scenarios:
        scenario_manager.add_scenario(scenario)

    return scenario_manager


class ChatBot(TemplateView):
    template_name = 'chatbot/index.html'


class RequestChat(View):
    def get(self, request, *args, **kwargs):
        url_pattern = self.kwargs['url_pattern']
        text = self.kwargs['text']
        uid = self.kwargs['uid']
        cache_key = uid
        scenario_manager = return_scenario()

        if url_pattern == 'request_chat':
            prep = dataset.load_predict(text, emb)
            intent = clf.predict(prep, calibrate=False)
            entity = rcn.predict(prep)
            text = dataset.prep.tokenize(text, train=False)

            scenario_result = scenario_manager.apply_scenario(intent, entity, text)
            print(scenario_result)

            cache.set(cache_key, scenario_result, 60 * 60)
            return JsonResponse(scenario_result)

        elif url_pattern == 'fill_slot':
            prep = dataset.load_predict(text, emb)
            entity = rcn.predict(prep)
            text = dataset.prep.tokenize(text, train=False)

            dialogue_cache = cache.get(cache_key, None)
            intent = dialogue_cache['intent']

            text = text + dialogue_cache['input']
            entity = entity + dialogue_cache['entity']
            scenario_result = scenario_manager.apply_scenario(intent, entity, text)
            return JsonResponse(scenario_result)



