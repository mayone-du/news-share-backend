import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from .models import Category, News, Tag, User


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


class Mutation(graphene.ObjectType):
    create_user = UserCreateMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Query(graphene.ObjectType):
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = DjangoFilterConnectionField(UserNode)

    @login_required
    def resolve_user(self, info, **kwargs):
        email = kwargs.get('email')
        return get_user_model().objects.get(id=from_global_id(id)[1])

    @login_required
    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()
