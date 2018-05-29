from rest_framework import serializers
from django.conf import settings
from apps.user.models import Referral, ReferralFeedback
from api.serializers.user import UserProfilePublicSer


class ReferralFeedbackSer(serializers.ModelSerializer):

    class Meta:
        model = ReferralFeedback


class ReferralSerializer(serializers.ModelSerializer):

    def validate_price(self, value):
        min_price = settings.PAYMENT['PRICE']['referral_min']
        """
        Check that the start is before the stop.
        """
        if value < min_price:
            raise serializers.ValidationError("Minimum price is {0}".format(min_price))
        return value

    user_model = UserProfilePublicSer(source='user', read_only=True)
    user_requester = serializers.SerializerMethodField()

    def get_user_requester(self, model):
        if model.cur_buy_request:
            return UserProfilePublicSer(model.cur_buy_request.user).data
        return None

    feedback = ReferralFeedbackSer(required=False, allow_null=True)

    #We don't want to show some fields if user hasn't bought this referral
    def to_representation(self, instance):
        fields_to_remove = ['email', 'phone', 'last_name', 'first_name']
        fields_to_remove_owner = ['user_bought', 'feedback']
        fields_to_remove_requester = ['user_requester']
        data = super(ReferralSerializer, self).to_representation(instance)
        try:
            user = self.context['request'].user
            #Logic when to remove fields_to_remove
            if instance.user_bought != user and instance.user != user:
                for field in fields_to_remove:
                    data.pop(field)
            #If not owner
            if instance.user != user:
                for field in fields_to_remove_owner:
                    data.pop(field)
            if user.id != data['user_requester'].id:
                for field in fields_to_remove_requester:
                    data.pop(field)

        except Exception as e:
            pass
        return data

    class Meta:
        model = Referral
        fields = ['first_name', 'last_name', 'email', 'phone', 'industry', 'price', 'income', 'hash',
                  'user', 'user_model', 'date_added', 'address', 'user_bought', 'feedback', 'note', 'user_requester',
                  'score']

        read_only_fields = ['hash']
