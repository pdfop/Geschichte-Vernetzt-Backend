from flask_graphql_auth import create_access_token, create_refresh_token, mutation_jwt_refresh_token_required, \
    get_jwt_identity, AuthInfoField, mutation_jwt_required
from graphene import ObjectType, Schema, List, Mutation, String, Field, Boolean, Union
from graphene_mongo import MongoengineObjectType
from werkzeug.security import generate_password_hash, check_password_hash
from models.Code import Code
from models.Admin import Admin as AdminModel

"""
GraphQL Schema for the admin web portal
includes all functionality of the portal: admin account creation and management, 
                                          account promotion code creation,
                                          object creation and management 
login creates a jwt access and refresh token. 
all other methods require a valid token

"""

# TODO: queries


class BooleanField(ObjectType):
    boolean = Boolean()


class ProtectedBool(Union):
    class Meta:
        types = (BooleanField, AuthInfoField)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)


class StringField(ObjectType):
    string = String()


class ProtectedString(Union):
    class Meta:
        types = (StringField, AuthInfoField)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)


class Admin(MongoengineObjectType):
    class Meta:
        model = AdminModel


class CreateAdmin(Mutation):
    class Arguments:
        username = String(required=True)
        password = String(required=True)
        teacher = Boolean()

    user = Field(lambda: Admin)
    ok = Boolean()

    def mutate(self, info, username, password):
        if not AdminModel.objects(username=username):
            user = AdminModel(username=username, password=generate_password_hash(password))
            user.save()
            return CreateAdmin(user=user, ok=True)
        else:
            return CreateAdmin(user=None, ok=False)


class PromoteUser(Mutation):
    class Arguments:
        token = String()
        code = String()

    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, info, code):
        username = get_jwt_identity()
        if not (Code.objects(code=code) and AdminModel.objects(username=username)):
            return PromoteUser(ok=BooleanField(boolean=False))
        else:

            Code.objects.delete(code=code)
            user = AdminModel.objects.get(username=username)
            user.teacher = True
            user.save()
            return PromoteUser(ok=BooleanField(boolean=True))


class ChangePassword(Mutation):
    class Arguments:
        token = String()
        password = String()

    ok = Field(ProtectedBool)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, password):
        username = get_jwt_identity()
        user = AdminModel.objects(username=username)[0]
        user.update(set__password=generate_password_hash(password))
        user.save()
        return ChangePassword(ok=BooleanField(boolean=True))


class Auth(Mutation):
    class Arguments:
        username = String(required=True)
        password = String(required=True)

    access_token = String()
    refresh_token = String()
    ok = Boolean()

    @classmethod
    def mutate(cls, _, info, username, password):
        if not (AdminModel.objects(username=username) and check_password_hash(
                AdminModel.objects(username=username)[0].password, password)):
            return Auth(ok=False)
        else:

            return Auth(access_token=create_access_token(username), refresh_token=create_refresh_token(username), ok=True)


class Refresh(Mutation):
    class Arguments(object):
        refresh_token = String()

    new_token = String()

    @classmethod
    @mutation_jwt_refresh_token_required
    def mutate(cls, info):
        current_user = get_jwt_identity()
        return Refresh(new_token=create_access_token(identity=current_user))


class Mutation(ObjectType):
    create_user = CreateAdmin.Field()
    auth = Auth.Field()
    refresh = Refresh.Field()
    change_password = ChangePassword.Field()
    promote_user = PromoteUser.Field()


class Query(ObjectType):
    users = List(Admin)
    user = List(Admin, username=String())

    def resolve_user(self, info, username):
        return list(AdminModel.objects.get(username=username))

    def resolve_users(self, info):
        return list(AdminModel.objects.all())


user_schema = Schema(query=Query, mutation=Mutation)
