from django.shortcuts import render

def doc_list(request):
    return render(request, 'documents/doc_list.html')

def doc_create(request):
    return render(request, 'documents/doc_form.html')

def doc_detail(request, pk):
    return render(request, 'documents/doc_detail.html')