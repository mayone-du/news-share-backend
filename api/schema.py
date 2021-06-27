import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from .models import Profile, Task, TestModel, User


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'is_staff': ['exact']
        }
        interfaces = (relay.Node,)


class UserCreateMutation(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=False)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        user = User(
            email=input.get('email'),
        )
        user.username = input.get('username')
        user.set_password(input.get('password'))
        user.save()

        return UserCreateMutation(user=user)


class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            'profile_name': ['exact', 'icontains'],
            'profile_text': ['exact', 'icontains']
        }
        interfaces = (relay.Node,)


class ProfileCreateMutation(relay.ClientIDMutation):
    class Input:
        profile_name = graphene.String(required=True)
        profile_text = graphene.String(required=False)

    profile = graphene.Field(ProfileNode)

    def mutate_and_get_payload(root, info, **input):
        profile = Profile(
            profile_name=input.get('profile_name'),
        )
        profile.target_user_id = info.context.user.id
        profile.profile_text = input.get('profile_text')
        profile.save()

        return ProfileCreateMutation(profile=profile)


class Mutation(graphene.ObjectType):
    create_user = UserCreateMutation.Field()
    create_profile = ProfileCreateMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Query(graphene.ObjectType):
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = DjangoFilterConnectionField(UserNode)
    profile = graphene.Field(ProfileNode, id=graphene.NonNull(graphene.ID))
    all_profiles = DjangoFilterConnectionField(ProfileNode)

    @login_required
    def resolve_user(self, info, **kwargs):
        email = kwargs.get('email')
        return get_user_model().objects.get(id=from_global_id(id)[1])

    @login_required
    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()

    @login_required
    def resolve_profile(self, info, **kwargs):
        id = kwargs.get('id')
        return Profile.objects.get(id=from_global_id(id)[1])

    @login_required
    def resolve_all_profiles(self, info, **kwargs):
        return Profile.objects.all()
