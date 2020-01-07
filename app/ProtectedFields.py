from flask_graphql_auth import AuthInfoField
from graphene import ObjectType, String, Boolean, Union

"""
collection of protected unions of various data types and jwt-auths's AuthInfoField
used in the Schemas to implement protected access to data 
"""


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
