from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .summary.crawler import summary_crawler
from .summary.infoList import VERIFIED_BLOG_LIST
from. summary.notion_crawler import notion_summary
"""
Comment

velog : 비공개 포스트 시 크롤링 불가
notion : 오른쪽 공유, 게시시 만 크롤링 가능 그 외 불가 
"""

@api_view(['POST'])
# Portfolio Summary View
def summary_view(request):
    if request.method == 'POST':
        try:
            print(request.data)
            blog = request.data.get('blog')
            
            if blog == "notion":
                uploaded_file = request.FILES.get("html")

                if not uploaded_file:
                    return Response({"Error": "No HTML file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
                
                file_name, file_extension = uploaded_file.name.split('.')
                
                if file_extension == "html":
                    notion_summary(uploaded_file)
                else:
                    raise Exception
            else:
                url = request.data.get('url')
                print(url)
                extract_content = summary_crawler(url, blog)

            return Response({"Success : Good Request"}, status=status.HTTP_200_OK)
        except:
            return Response({"Error : Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error" : 'Only Post requests are allowed'}, status=status.HTTP_400_BAD_REQUEST)

