from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import JobDescription, JobDescriptionSerializer, ResumeSerializer, Resume
from .analazer import process_resume
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect

class JobDescriptionAPI(APIView):
    def get(self, request):
        queryset= JobDescription.objects.all()
        serializers = JobDescriptionSerializer(queryset, many = True)
        return Response({
            'status':True,
            'data': serializers.data 
        })
        

class AnalyzeResumeAPI(APIView):
    def post(self, request):
        try:
            data= request.data
            if not data.get('job_description'):
                return Response({
                    'status':False,
                    'message':"job descrition is long",
                    'data':{}
                })
            serializer = ResumeSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    'status':False,
                    'message':'errors',
                    'data':serializer.errors   
                })
            
            serializer.save()
            _data =serializer.data
            resume_instance=Resume.objects.get(id=_data['id'])
            resume_path =resume_instance.resume.path
            data = process_resume(resume_path, 
                                  JobDescription.objects.get(id=data.get('job_description')).job_description
                                  )
            return Response({
                    'status':True,
                    'message':'Resume Analyzed',
                    'data':data  
                })

        except Exception as e:
            return Response({
                'data':False
            })
            
            
@csrf_exempt
def resume_rank_view(request):
    context = {}
    if request.method == "POST":
        try:
            job_description = request.POST.get("job_description")
            resume_file = request.FILES["resume"]

            if not job_description or not resume_file:
                context["error"] = "Please provide both job description and resume."
                return render(request, "analyze_resume.html", context)

            fs = FileSystemStorage()
            filename = fs.save(resume_file.name, resume_file)
            resume_path = fs.path(filename)

            from .analazer import process_resume
            result = process_resume(resume_path, job_description)

            if result:
                context["result"] = result
            else:
                context["error"] = "Something went wrong while processing your resume."

        except Exception as e:
            context["error"] = str(e)

    return render(request, "analyze_resume.html", context)