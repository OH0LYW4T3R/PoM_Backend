from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .summary.crawler import summary_crawler
from .summary.infoList import VERIFIED_BLOG_LIST
"""
Comment

velog : 비공개 포스트 시 크롤링 불가
"""

@api_view(['POST'])
# Portfolio Summary View
def summary_view(request):
    if request.method == 'POST':
        try:
            print(request.data)
            url = request.data.get('url')
            blog = request.data.get('blog')
            print(url)
            
            extract_content = summary_crawler(url, "velog")


            return Response({"Success : Good Request"}, status=status.HTTP_200_OK)
        except:
            return Response({"Error : Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"Error" : 'Only Post requests are allowed'}, status=status.HTTP_400_BAD_REQUEST)

