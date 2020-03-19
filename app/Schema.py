from app.WebMutations import Mutation as WebMutation
from app.WebQueries import Query as WebQuery
from app.AppMutations import Mutation as AppMutation
from app.AppQueries import Query as AppQuery
from graphene import Schema

"""
    This class simply combines the mutation and query classes to create the graphql schemas for the web and app endpoints 
"""

app_schema = Schema(mutation=AppMutation, query=AppQuery)
web_schema = Schema(mutation=WebMutation, query=WebQuery)
