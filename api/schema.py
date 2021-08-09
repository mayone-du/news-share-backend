import datetime

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
        contributor_name = graphene.String(required=False)
        created_at = graphene.Int(required=True)

    news = graphene.Field(NewsNode)

    def mutate_and_get_payload(root, info, **input):
        news = News(
            url=input.get('url'),
            contributor_name=input.get('contributor_name'),
        )

        # 作成日時をタイムUNIXタイムスタンプ形式で受け取り設定
        if input.get('created_at') is not None:
            now = datetime.datetime.fromtimestamp(input.get('created_at'))
            news.created_at = now

        # スクレイピングでOGPの内容を取得
        html = requests.get(input.get('url'))
        # HTMLをパース
        parsed_html = BeautifulSoup(html.content, 'html.parser')
        if parsed_html is not None:
            # OGPのタイトルがある場合
            og_title_tag = parsed_html.find(
                'meta', attrs={'property': 'og:title', 'content': True})
            if og_title_tag is not None:
                og_title = og_title_tag.get('content')
                news.title = og_title
            else:
                news.title = parsed_html.find('title').text

            # OGPのディスクリプションがある場合
            og_description_tag = parsed_html.find(
                'meta', attrs={'property': 'og:description', 'content': True})
            if og_description_tag is not None:
                og_description = og_description_tag.get('content')
                news.summary = og_description
            # OGPの画像がある場合
            og_image_tag = parsed_html.find(
                'meta', attrs={'property': 'og:image', 'content': True})
            if og_image_tag is not None:
                og_image = og_image_tag.get('content')
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


class UpdateNewsMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        created_at = graphene.Int(required=True)

    news = graphene.Field(NewsNode)

    def mutate_and_get_payload(root, info, **input):
        news = News.objects.get(id=from_global_id(input.get('id'))[1])

        # ニュースのシェアする時間を明日に延期
        news.created_at = datetime.datetime.fromtimestamp(
            input.get('created_at', ))

        news.save()
        return UpdateNewsMutation(news=news)


class Mutation(graphene.ObjectType):
    create_user = CreateUserMutation.Field()
    create_category = CreateCategoryMutation().Field()
    create_tag = CreateTagMutation().Field()
    create_news = CreateNewsMutation().Field()
    update_news = UpdateNewsMutation().Field()
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
    today_news = DjangoFilterConnectionField(NewsNode)
    # specific_day_news = DjangoFilterConnectionField(NewsNode)

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

    # 全てのニュースを取得
    def resolve_all_news(self, info, **kwargs):
        return News.objects.all()

    # 今日のニュースを取得
    def resolve_today_news(self, info, **kwargs):
        today = datetime.datetime.today()
        return News.objects.filter(created_at__year=today.year, created_at__month=today.month, created_at__day=today.day)

    # TODO: なぜか動かない
    # def resolve_specific_day_news(self, info, **kwargs):
    #     day = str(kwargs.get('created_at'))[:10]
    #     parsed_day = datetime.datetime.strptime(
    #         day, '%Y-%m-%d')
    #     return News.objects.filter(created_at__year=parsed_day.year, created_at__month=parsed_day.month, created_at__day=parsed_day.day)
