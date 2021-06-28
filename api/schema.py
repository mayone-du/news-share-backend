import graphene
import graphql_jwt
import requests
from bs4 import BeautifulSoup
from decouple import config
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
            'email': ['exact', 'icontains'],
            'is_staff': ['exact']
        }
        interfaces = (relay.Node,)


class CreateUserMutation(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=False)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        user = User(
            email=input.get('email'),
            username=input.get('username')
        )
        user.set_password(input.get('password'))
        user.save()

        return CreateUserMutation(user=user)


class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        filter_fields = {
            'category_name': ['exact', 'icontains']
        }
        interfaces = (relay.Node,)


class CreateCategoryMutation(relay.ClientIDMutation):
    class Input:
        category_name = graphene.String(required=True)

    category = graphene.Field(CategoryNode)

    def mutate_and_get_payload(root, info, **input):
        category = Category(
            category_name=input.get('category_name'),
        )
        return CreateCategoryMutation(category=category)


class TagNode(DjangoObjectType):
    class Meta:
        model = Tag
        filter_fields = {
            'tag_name': ['exact', 'icontains']
        }
        interfaces = (relay.Node,)


class CreateTagMutation(relay.ClientIDMutation):
    class Input:
        tag_name = graphene.String(required=True)

    tag = graphene.Field(TagNode)

    def mutate_and_get_payload(root, info, **input):
        tag = Tag(
            tag_name=input.get('tag_name'),
        )
        return CreateTagMutation(tag=tag)


class NewsNode(DjangoObjectType):
    class Meta:
        model = News
        filter_fields = {
            'url': ['exact'],
            'title': ['exact', 'icontains'],
            'summary': ['exact', 'icontains'],
            'created_at': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class CreateNewsMutation(relay.ClientIDMutation):
    class Input:
        select_category_id = graphene.ID(required=False)
        url = graphene.String(required=True)
        tag_ids = graphene.List(graphene.ID)

    news = graphene.Field(NewsNode)

    def mutate_and_get_payload(root, info, **input):
        news = News(
            url=input.get('url'),
        )

        # スクレイピングでOGPの内容を取得
        # TODO: エラーハンドリング
        html = requests.get(input.get('url')).text
        parsed_html = BeautifulSoup(html, 'html.parser')
        # OGPのタイトルがある場合
        if parsed_html.find(
                'meta', attrs={'property': 'og:title', 'content': True}).get('content') is not None:
            og_title = parsed_html.find(
                'meta', attrs={'property': 'og:title', 'content': True}).get('content')
            news.title = og_title
        # OGPのディスクリプションがある場合
        if parsed_html.find(
                'meta', attrs={'property': 'og:description', 'content': True}).get('content') is not None:
            og_description = parsed_html.find(
                'meta', attrs={'property': 'og:description', 'content': True}).get('content')
            news.summary = og_description
        # OGPの画像がある場合
        if parsed_html.find(
                'meta', attrs={'property': 'og:image', 'content': True}).get('content') is not None:
            og_image = parsed_html.find(
                'meta', attrs={'property': 'og:image', 'content': True}).get('content')
            news.image_path = og_image

        news.save()

        if input.get('select_category_id') is not None:
            news.select_category_id = from_global_id(
                input.get('select_category_id'))[1],

        tag_set = []
        if input.get('tag_ids') is not None:
            for tag_id in input.get('tag_ids'):
                tag_set.append(tag_id)
            news.tags = tag_set
        news.save()
        return CreateNewsMutation(news=news)


class Mutation(graphene.ObjectType):
    create_user = CreateUserMutation.Field()
    create_category = CreateCategoryMutation().Field()
    create_tag = CreateTagMutation().Field()
    create_news = CreateNewsMutation().Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


class Query(graphene.ObjectType):
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = DjangoFilterConnectionField(UserNode)
    category = graphene.Field(CategoryNode, id=graphene.NonNull(graphene.ID))
    all_categories = DjangoFilterConnectionField(CategoryNode)
    tag = graphene.Field(TagNode, id=graphene.NonNull(graphene.ID))
    all_tags = DjangoFilterConnectionField(TagNode)
    news = graphene.Field(NewsNode, id=graphene.NonNull(graphene.ID))
    all_news = DjangoFilterConnectionField(NewsNode)

    @ login_required
    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        return get_user_model().objects.get(id=from_global_id(id)[1])

    @ login_required
    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()

    def resolve_category(self, info, **kwargs):
        id = kwargs.get('id')
        return Category.objects.get(id=from_global_id(id)[1])

    def resolve_all_categories(self, info, **kwargs):
        return Category.objects.all()

    def resolve_tag(self, info, **kwargs):
        id = kwargs.get('id')
        return Tag.objects.get(id=from_global_id(id)[1])

    def resolve_all_tags(self, info, **kwargs):
        return Tag.objects.all()

    def resolve_news(self, info, **kwargs):
        id = kwargs.get('id')
        return News.objects.get(id=from_global_id(id)[1])

    def resolve_all_news(self, info, **kwargs):
        return News.objects.all()
