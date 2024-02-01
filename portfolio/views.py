from django.shortcuts import render
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

def copy_request_data(data):
    req_data = {}

    print(data)
    for key, value in data.items():
        req_data[key] = value

    return req_data

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

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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
        """
        user_id = request.data.get('user_id')
        category = request.data.get('category')
        category_obj = Category.objects.filter(user_id=user_id, category=category)
        
        if category_obj.exists():
            req_data = copy_request_data(request.data)
            req_data["category_id"] = category_obj[0].id 

            thumbnail = request.data.get("thumbnail")
            if thumbnail == "None":
                pass
            else:
                req_data["thumbnail"] = thumbnail

            serializer = self.get_serializer(data=req_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)    
        else:
            return Response({"Error : Not exist Category"}, status=status.HTTP_400_BAD_REQUEST)
        

    