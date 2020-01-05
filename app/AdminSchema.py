from flask_graphql_auth import create_access_token, create_refresh_token, mutation_jwt_refresh_token_required, \
    get_jwt_identity, AuthInfoField, mutation_jwt_required
from graphene import ObjectType, Schema, List, Mutation, String, Field, Boolean, Union, Int
from graphene_mongo import MongoengineObjectType
from werkzeug.security import generate_password_hash, check_password_hash
from models.Admin import Admin as AdminModel
from models.MuseumObject import MuseumObject as MuseumObjectModel
from models.Code import Code as CodeModel
from models.User import User as UserModel
import string
import random
from .ProtectedFields import StringField, ProtectedString, BooleanField, ProtectedBool
from .UserSchema import User

"""
GraphQL Schema for the admin web portal
includes all functionality of the portal: admin account creation and management, 
                                          account promotion code creation,
                                          user demotion and deletion, 
                                          object creation and management 
login creates a jwt access and refresh token. 
all other methods require a valid token

"""


class MuseumObject(MongoengineObjectType):
    class Meta:
        model = MuseumObjectModel


class ProtectedMuseumObject(Union):
    class Meta:
        types = (MuseumObject, AuthInfoField)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)


class CreateMuseumObject(Mutation):
    class Arguments:
        object_id = Int(required=True)
        category = String(required=True)
        sub_category = String(required=True)
        title = String(required=True)
        token = String(required=True)
        year = Int()
        picture = String()
        art_type = String()
        creator = String()
        material = String()
        size = String()
        location = String()
        description = String()
        interdisciplinary_context = String()

    museum_object = Field(lambda: MuseumObject)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id, category, sub_category, title, **kwargs):
        year = kwargs.get('year', None)
        picture = kwargs.get('picture', None)
        art_type = kwargs.get('art_type', None)
        creator = kwargs.get('creator', None)
        material = kwargs.get('material', None)
        size = kwargs.get('size', None)
        location = kwargs.get('location', None)
        description = kwargs.get('description', None)
        interdisciplinary_context = kwargs.get('interdisciplinary_context', None)
        if not MuseumObjectModel.objects(object_id=object_id):
            museum_object = MuseumObjectModel(object_id=object_id, category=category, sub_category=sub_category,
                                              title=title, year=year, picture=picture, art_type=art_type,
                                              creator=creator, material=material, size=size, location=location,
                                              description=description,
                                              interdisciplinary_context=interdisciplinary_context)
            museum_object.save()
            return CreateMuseumObject(ok=BooleanField(boolean=True), museum_object=museum_object)
        else:
            return CreateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)


class UpdateMuseumObject(Mutation):
    class Arguments:
        object_id = Int(required=True)
        token = String(required=True)
        category = String()
        sub_category = String()
        title = String()
        year = Int()
        picture = String()
        art_type = String()
        creator = String()
        material = String()
        size = String()
        location = String()
        description = String()
        interdisciplinary_context = String()

    museum_object = Field(lambda: MuseumObject)
    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, object_id, **kwargs):

        if not MuseumObjectModel.objects(object_id=object_id):
            return UpdateMuseumObject(ok=BooleanField(boolean=False), museum_object=None)
        else:
            museum_object = MuseumObjectModel.objects(object_id=object_id)[0]

            category = kwargs.get('category', None)
            sub_category = kwargs.get('sub_category', None)
            title = kwargs.get('title',None)
            year = kwargs.get('year', None)
            picture = kwargs.get('picture', None)
            art_type = kwargs.get('art_type', None)
            creator = kwargs.get('creator', None)
            material = kwargs.get('material', None)
            size = kwargs.get('size', None)
            location = kwargs.get('location', None)
            description = kwargs.get('description', None)
            interdisciplinary_context = kwargs.get('interdisciplinary_context', None)

            if category is not None:
                museum_object.update(set__category=category)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if sub_category is not None:
                museum_object.update(set__sub_category=sub_category)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if title is not None:
                museum_object.update(set__title=title)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if year is not None:
                museum_object.update(set__year=year)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if picture is not None:
                museum_object.update(set__picture=picture)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if art_type is not None:
                museum_object.update(set__art_type=art_type)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if creator is not None:
                museum_object.update(set__creator=creator)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if material is not None:
                museum_object.update(set__material=material)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if size is not None:
                museum_object.update(set__size=size)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if location is not None:
                museum_object.update(set__location=location)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if description is not None:
                museum_object.update(set__description=description)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]
            if interdisciplinary_context is not None:
                museum_object.update(set__interdisciplinary_context=interdisciplinary_context)
                museum_object.save()
                museum_object = MuseumObjectModel.objects(object_id=object_id)[0]


            return UpdateMuseumObject(ok=BooleanField(boolean=True), museum_object=museum_object)


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

            return Auth(access_token=create_access_token(username), refresh_token=create_refresh_token(username),
                        ok=True)


class Refresh(Mutation):
    class Arguments(object):
        refresh_token = String()

    new_token = String()

    @classmethod
    @mutation_jwt_refresh_token_required
    def mutate(cls, info):
        current_user = get_jwt_identity()
        return Refresh(new_token=create_access_token(identity=current_user))


class Code(MongoengineObjectType):
    class Meta:
        model = CodeModel


class CreateCode(Mutation):
    class Arguments:
        token = String(required=True)
    ok = ProtectedBool()
    code = ProtectedString()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info):
        letters = string.ascii_lowercase
        code_string = ''.join(random.choice(letters) for i in range(5))
        code = CodeModel(code=code_string)
        code.save()
        return CreateCode(ok=BooleanField(boolean=True), code=StringField(string=code_string))


class DemoteUser(Mutation):
    class Arguments:
        username = String(required=True)
        token = String(required=True)

    ok = ProtectedBool()
    user = Field(User)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, username):
        user = UserModel.objects.get(username=username)
        user.update(set__teacher=False)
        user.save()
        user = UserModel.objects.get(username=username)
        return DemoteUser(ok=BooleanField(boolean=True), user=user)


class DeleteUser(Mutation):
    class Arguments:
        username = String(required=True)
        token = String(required=True)

    ok = ProtectedBool()

    @classmethod
    @mutation_jwt_required
    def mutate(cls, _, info, username):
        user = UserModel.objects.get(username=username)
        user.delete()
        return DeleteUser(ok=BooleanField(boolean=True))


class Mutation(ObjectType):
    create_user = CreateAdmin.Field()
    auth = Auth.Field()
    refresh = Refresh.Field()
    change_password = ChangePassword.Field()
    create_museum_object = CreateMuseumObject.Field()
    update_museum_object = UpdateMuseumObject.Field()
    create_code = CreateCode.Field()
    demote_user = DemoteUser.Field()
    delete_user = DeleteUser.Field()


class Query(ObjectType):
    users = List(Admin)
    user = List(Admin, username=String())
    objects = List(MuseumObject, object_id=Int())

    def resolve_objects(self, info, object_id):
        return list(MuseumObjectModel.objects.get(object_id=object_id))

    def resolve_user(self, info, username):
        return list(AdminModel.objects.get(username=username))

    def resolve_users(self, info):
        return list(AdminModel.objects.all())


admin_schema = Schema(query=Query, mutation=Mutation)
