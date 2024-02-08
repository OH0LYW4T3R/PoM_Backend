from config.settings import BASE_DIR
from collections import defaultdict

import os
import requests

from django.shortcuts import render
from django.core.files import File
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets

from .summary.velog_crawler import velog_crawler
from .summary.infoList import VERIFIED_BLOG_LIST
from .summary.notion_crawler import notion_crawler
from .summary.tistory_crawler import tistory_crawler  
from .summary.github_crawler import github_crawler 
from .summary.GPT_summary import add_question, gpt_summary

from .serializers import SummarySerializer
from .serializers import UserSerializer, EnterpriseUserSerializer, EnterpriseSerializer, CategorySerializer, PortfolioSerializer, SummarySerializer

from .models import User, EnterpriseUser, Enterprise, Category, Portfolio
"""
Comment

velog : 비공개 포스트 시 크롤링 불가
tistory : 문제 없음
notion : 노션은 우측 상단 ... 에서 내보내기 후 압축파일 해제, html파일 넣어줘야함.
github : Readme.md 파일을 받아서 올려줘야함

naver : 크롤링 막음.
"""
ADDRESS = "http://127.0.0.1:8000/"
# 추후 로그인 서버 주소 삽입
LOGIN_URL = "http://127.0.0.1:8000/p/"

def copy_request_data(data):
    req_data = {}

    print(data)
    for key, value in data.items():
        req_data[key] = value

    return req_data

def get_user_id(request):
    authorization_header = request.headers.get('Authorization', '')

    if authorization_header.startswith('Bearer '):
        jwt_token = authorization_header[len('Bearer '):]

        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(LOGIN_URL, headers=headers)

        if response.status_code == 200:
            # 추후 응답에 따른 로직 변경
            response_data = response.json()
            return response_data['user_id'], response_data['user_type'], response_data['company']
        else:
            # Server Error
            return -2, None, None
    else:
        # -1 : Not Found (JWT)
        return -1, None, None
    
test_enterprise_code = {
    "a1b1" : "카카오",
    "a2b2" : "네이버",
    "a3b3" : "배달의민족",
    "a4b4" : "라인",
    "a5b5" : "쿠팡",
    "a6b6" : "당근",
    "a7b7" : "토스"
}

@api_view(['POST'])
# Portfolio Summary View
def summary_view(request):
    if request.method == 'POST':
        try:
            print(request.data)
            blog = request.data.get('blog')
            extract_content = None
            
            # 파일 영역
            if blog == "notion" or blog == "github":
                uploaded_file = request.FILES.get("file")

                if not uploaded_file:
                    return Response({"Error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
                
                file_name, file_extension = uploaded_file.name.split('.')

                if file_extension == "html":
                    extract_content = notion_crawler(uploaded_file, blog)
                elif file_extension == "md":
                    extract_content = github_crawler(uploaded_file)
                else:
                    raise Exception
                
            # url 영역
            elif blog == "velog" or blog == "tistory":
                url = request.data.get('url')
                
                # url, blog
                if blog == "velog":
                    extract_content = velog_crawler(url, blog)
                elif blog == "tistory":
                    extract_content = tistory_crawler(url, blog)
            else:
                return Response({"Error : Blog Select Error"}, status=status.HTTP_400_BAD_REQUEST)

            total_question = add_question(extract_content)
            gpt_response = gpt_summary(total_question, extract_content[0], extract_content[2])

            serializer = SummarySerializer(data=gpt_response)

            if serializer.is_valid():
                serializer_data = serializer.data
                print(serializer_data)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"Error : Serializer Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            return Response({"Error : Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error" : 'Only Post requests are allowed'}, status=status.HTTP_400_BAD_REQUEST)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class EnterpriseUserViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseUser.objects.all()
    serializer_class = EnterpriseUserSerializer

class EnterpriseViewSet(viewsets.ModelViewSet):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # 추후 서버로 보내는 코드로 변경
            # 기업이 코드를 만들때,
            # 포트폴리오를 봐야할 기간을 지정하도록 함
            code = request.data.get("enterprise_code")
            enterprise = test_enterprise_code[code]
            
            if enterprise:
                enterprise_obj = Enterprise.objects.filter(user_id=user_id, enterprise=enterprise)
                if not enterprise_obj.exists():
                    req_data = copy_request_data(request.data)
                    req_data["enterprise"] = enterprise
                    req_data["deadline"] = request.data.get("deadline")
                    req_data["user_id"] = user_id

                    serializer = self.get_serializer(data=req_data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    headers = self.get_success_headers(serializer.data)
                    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                else:
                    return Response({"Error : Already register"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Error : Enterprise not register Or typo"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            queryset = self.filter_queryset(self.get_queryset().filter(user_id=user_id))

            # 바로 반영이 안되므로 
            for query in queryset:
                print(query.deadline)
                if query.deadline < timezone.now():
                    print("call")
                    Enterprise.objects.filter(id=query.id).delete()
            
            queryset = Enterprise.objects.filter(user_id=user_id)
            #queryset = self.filter_queryset(self.get_queryset().filter(user_id=user_id))

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            enterprise_obj = Enterprise.objects.filter(user_id=user_id, id=kwargs.get("pk"))

            if enterprise_obj.exists():
                self.perform_destroy(enterprise_obj)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"Error : Enterprise not Exist"}, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            category_obj = Category.objects.filter(user_id=user_id, category=request.data.get("category"))

            if not category_obj.exists():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"Error : Category Already Exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            queryset = self.filter_queryset(self.get_queryset().filter(user_id=user_id))
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            category_obj = Category.objects.filter(id=kwargs.get("pk"))

            if category_obj.exists():
                serializer = self.get_serializer(category_obj[0])
                return Response(serializer.data)
            else:
                return Response({"Category Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            category_obj = Category.objects.filter(id=kwargs.get("pk"), user_id=user_id)

            if category_obj.exists():
                instance = self.get_object()
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"Error : No Access"}, status=status.HTTP_403_FORBIDDEN)
   
    def update(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            category_obj = Category.objects.filter(id=kwargs.get("pk"), user_id=user_id)

            if category_obj.exists():
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                return Response(serializer.data)
            else:
                return Response({"Error : No Access"}, status=status.HTTP_403_FORBIDDEN)
    
class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

    """
    jwt를 전달받고, 해당 jwt를 민재 로그인서버에 주고 유저 아이디를 받아온다.
    """
    def create(self, request, *args, **kwargs):
        """
        jwt_token = request.data.get('token')
        해당 토큰을 로그인 서버에 보내서 user_id 획득
        user_id = get_user_id(request)
        """
        user_id = request.data.get('user_id')

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            category = request.data.get('category')
            user_obj = User.objects.filter(id=user_id)
            category_obj = Category.objects.filter(user_id=user_id, category=category)

            if not category_obj.exists():
                Category.objects.create(user_id=user_obj[0], category=category)

            req_data = copy_request_data(request.data)
            req_data["category_id"] = category_obj[0].id 

            thumbnail_url = request.data.get("thumbnail_url")
            thumbnail_file = request.data.get("thumbnail_file")

            if thumbnail_file:
                req_data["thumbnail_file"] = thumbnail_file
            elif thumbnail_url:
                req_data["thumbnail_url"] = thumbnail_url

            req_data["name"] = user_obj[0].name
            # 프론트에서 thumbnail_url = '' && thumbnail_file = null 이면 그냥 기본이미지 보여주게 셋팅

            serializer = self.get_serializer(data=req_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers) 
        
    def list(self, request, *args, **kwargs):
        """
        jwt_token = request.data.get('token')
        해당 토큰을 로그인 서버에 보내서 user_id 획득
        user_id = get_user_id(request)
        """
        user_id = request.data.get("user_id")
        user_type = request.data.get("user_type")
        search_range = request.GET.get('search_range', None)

        # 다른사람도 볼수있게 해놨을때 로직도 생성
        if user_type == "i":
            if user_id == -1:
                return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            elif user_id == -2:
                return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                if search_range == "self":
                    category_obj = Category.objects.filter(user_id=user_id)

                    if category_obj.exists():
                        portfolio_queryset = Portfolio.objects.filter(category_id=category_obj[0].id)

                        for i in range(1, len(category_obj)):
                            queryset = Portfolio.objects.filter(category_id=category_obj[i].id)
                            portfolio_queryset = portfolio_queryset.union(queryset)

                        serializer = self.get_serializer(portfolio_queryset, many=True)
                        return Response(serializer.data)
                    else:
                        return Response({"Error : Not Exist Portfolio"}, status=status.HTTP_400_BAD_REQUEST)
                elif search_range == "other":
                    queryset = self.filter_queryset(self.get_queryset().filter(personal_visible="public"))

                    page = self.paginate_queryset(queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)

                    serializer = self.get_serializer(queryset, many=True)
                    return Response(serializer.data)
                else:
                    return Response({"Error : Wrong Search Range"}, status=status.HTTP_400_BAD_REQUEST)

        elif user_type == "e":
            company = request.data.get("company")
            register_user = User.objects.filter(enterprise_visible__enterprise=company)

            if register_user.exists():
                export_queryset = Portfolio.objects.none()
                name_list = []

                for user in register_user:
                    category_obj = Category.objects.filter(user_id=user.id)
                    name_list.append(user.name)
                    if category_obj.exists():
                        portfolio_queryset = Portfolio.objects.filter(category_id=category_obj[0].id)

                        for i in range(1, len(category_obj)):
                            queryset = Portfolio.objects.filter(category_id=category_obj[i].id)
                            portfolio_queryset = portfolio_queryset.union(queryset)

                        export_queryset = export_queryset.union(portfolio_queryset)

                serializer = self.get_serializer(export_queryset, many=True)

                refactoring = defaultdict(list)
                for item in serializer.data:
                    refactoring[item['name']].append(dict(item))

                name_data = [{name: data} for name, data in refactoring.items()]

                return Response(name_data, status=status.HTTP_200_OK)
            else:
                return Response({"Nobody user Registered"}, status=status.HTTP_200_OK)
        else:
            return Response({"Error : Type not Register"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        user_id = get_user_id(request)
        """
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            category_obj = Category.objects.filter(user_id=user_id)

            if category_obj:
                portfolio = None
                for category in category_obj:
                    portfolio = Portfolio.objects.filter(category_id=category.id, id=kwargs.get('pk'))
                    if portfolio.exists(): 
                        break
                
                if portfolio:
                    serializer = self.get_serializer(portfolio[0])
                    return Response(serializer.data)
                else:
                    return Response({"Error : Portfolio Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Error : User Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        
    def update(self, request, *args, **kwargs):
        """
        jwt_token = request.data.get('token')
        해당 토큰을 로그인 서버에 보내서 user_id 획득
        user_id = get_user_id(request)
        """
        user_id = request.data.get('user_id')
        category = request.data.get('category')
        category_obj = Category.objects.filter(user_id=user_id, category=category)
        
        if category_obj.exists():
            req_data = copy_request_data(request.data)
            req_data["category_id"] = category_obj[0].id
            req_data["upload_date"] = timezone.now()
            portfolio_obj = Portfolio.objects.filter(id=kwargs.get('pk'))

            if portfolio_obj.exists():
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=req_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"Error : Wrong URL Id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error : Not exist Category or No Access"}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request, *args, **kwargs):
        """
        user_id = get_user_id(request)
        """
        user_id = request.data.get("user_id")

        if user_id == -1:
            return Response({"Error : JWT Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id == -2:
            return Response({"Error : Login Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            category_obj = Category.objects.filter(user_id=user_id)

            if category_obj.exists():
                portfolio = None
                for category in category_obj:
                    portfolio = Portfolio.objects.filter(category_id=category.id, id=kwargs.get('pk'))
                    if portfolio.exists(): 
                        break
                
                if portfolio:
                    self.perform_destroy(portfolio[0])
                    return Response({"Delete Success"},status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({"Error : Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"Error : User Not Found"}, status=status.HTTP_400_BAD_REQUEST)