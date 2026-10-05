from django.urls import path

from apps.voxum_base.views_process_file import (
    CreateExcelWorkerApi,
    ErrorFileDetailApi,
    ErrorFileListApi,
    ExcelWorkerDetailApi,
    ExcelWorkerListApi,
    WorkerExampleDetailApi,
    WorkerExampleNamesApi,
)


urlpatterns = [
    path('create/<str:path>/<str:name>/', CreateExcelWorkerApi.as_view()),
    path('detail/<uuid:id>/', ExcelWorkerDetailApi.as_view()),
    path('list/<uuid:object_id>/', ExcelWorkerListApi.as_view()),
    path('errors/<uuid:file_id>/', ErrorFileListApi.as_view()),
    path('error/detail/<uuid:id>/', ErrorFileDetailApi.as_view()),
    path('examples/name/', WorkerExampleNamesApi.as_view()),
    path('examples/detail/<str:name>/', WorkerExampleDetailApi.as_view()),
]
