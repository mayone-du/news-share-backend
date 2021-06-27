import graphene
from graphene_django.types import DjangoObjectType
from .models import User, Profile, Task, TestModel
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from graphql_relay import from_global_id
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
import graphql_jwt
from graphene_file_upload.scalars import Upload

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
        # target_user = graphene.ID
        profile_name = graphene.String(required=True)
        profile_text = graphene.String(required=False)

    profile = graphene.Field(ProfileNode)

    def mutate_and_get_payload(root, info, **input):
        profile = Profile(
            profile_name=input.get('profile_name'),
        )
        profile.profile_text = input.get('profile_text')
        profile.save()

        return ProfileCreateMutation(profile=profile)


class TaskNode(DjangoObjectType):
    class Meta:
        model = Task
        filter_fields = {
            'title': ['exact', 'icontains'],
            'content': ['exact', 'icontains'],
            'is_completed': ['exact'],
            'create_user': ['exact'],
        }
        interfaces = (relay.Node,)


class TaskCreateMutation(relay.ClientIDMutation):
# class TaskCreateMutation(graphene.Mutation):
    class Input:
        title = graphene.String(required=True)
        content = graphene.String(required=False)
        is_completed = graphene.Boolean(required=True)
        create_user = graphene.ID(required=False)
        thumbnail = Upload(required=False)

    task = graphene.Field(TaskNode)

    def mutate_and_get_payload(root, info, **input):

        task = Task(
            title=input.get('title'),
        )

        task.content = input.get('content')
        task.is_completed = input.get('is_completed')
        # print(input)
        task.thumbnail = input.get('thumbnail')
        # task.thumbnail = root.Input.thumbnail
        # print(Task.objects.get(title='テスト').thumbnail)
        # task.thumbnail = Upload
        # task.thumbnail = Task.objects.get(title='テスト').thumbnail
        # task.thumbnail = Task.thumbnail
        # task.create_user = User.objects.get(id='VXNlck5vZGU6MQ==')
        # task.create_user = User.objects.get(id=from_global_id(input.get('create_user'))[1])
        task.create_user = User.objects.get(id=from_global_id(input.get('create_user'))[1])
        task.save()

        return TaskCreateMutation(task=task)


# ! Test
class TestModelNode(DjangoObjectType):
    class Meta:
        model = TestModel
class TestMutation(graphene.Mutation):
    class Arguments:
        file = Upload()
        text = graphene.String(required=True)


    test = graphene.Field(TestModelNode)
    success = graphene.Boolean()

    def mutate(self, info, file, text):
        # print(text)
        test = TestModel(text=text)
        test.image = file
        # test.text = text
        test.save()
        return TestMutation(success=True)



# class TaskCreateMutation(graphene.Mutation):
# # class TaskCreateMutation(graphene.Mutation):
#     class Arguments:
#         thumbnail = Upload(required=False)
#         title = graphene.String(required=True)
#         content = graphene.String(required=False)
#         is_completed = graphene.Boolean(required=True)
#         create_user = graphene.ID(required=False)
#         id = graphene.ID(required=False)

#     success = graphene.Boolean()
#     task = graphene.Field(TaskNode)    

#     def mutate(self, info, thumbnail, title, content, is_completed, create_user, id):
#         # task = Task.objects.get(pk=from_global_id(id)[1])
#         print(title)
#         task = Task.objects.get(pk=id)
#         task.title = title
#         task.content = content
#         task.is_completed = is_completed
#         task.thumbnail = thumbnail
#         task.create_user = User.objects.get(id=from_global_id(create_user)[1])
#         task.save()

#         return TaskCreateMutation(success=True)

    # def mutate_and_get_payload(root, info, **input):

        # task = Task(
            # title=input.get('title'),
        # )

        # task.content = input.get('content')
        # task.is_completed = input.get('is_completed')
        # task.thumbnail = root.Input.thumbnail
        # print(Task.objects.get(title='テスト').thumbnail)
        # task.thumbnail = Upload
        # task.thumbnail = Task.objects.get(title='テスト').thumbnail
        # task.thumbnail = Task.thumbnail
        # task.create_user = User.objects.get(id='VXNlck5vZGU6MQ==')
        # task.create_user = User.objects.get(id=from_global_id(input.get('create_user'))[1])
        # task.create_user = User.objects.get(id=from_global_id(input.get('create_user'))[1])
        # task.save()

        # return TaskCreateMutation(task=task)


class TaskUpdateMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        is_completed = graphene.Boolean(required=True)

    task = graphene.Field(TaskNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):

        task = Task(
            id=from_global_id(input.get('id'))[1]
        )
        task.title = input.get('title')
        task.content = input.get('content')
        task.is_completed = input.get('is_completed')

        task.save()

        return TaskUpdateMutation(task=task)


class TaskDeleteMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    task = graphene.Field(TaskNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):

        task = Task(
            id=from_global_id(input.get('id'))[1]
        )
        task.delete()

        return TaskDeleteMutation(task=None)


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

