from app.WebMutations import Mutation as WebMutation
from app.WebQueries import Query as WebQuery
from app.AppMutations import Mutation as AppMutation
from app.AppQueries import Query as AppQuery
from graphene import Schema

app_schema = Schema(mutation=AppMutation, query=AppQuery)
web_schema = Schema(mutation=WebMutation, query=WebQuery)
