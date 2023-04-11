from django.shortcuts import render
from django.http import HttpResponse
from .models import Product
from .forms import ProductForm

# Create your views here.
def index(request):
    return HttpResponse("hello world")

def products(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, "myapp/index.html", context)

def product_detail(request, id):
    product = Product.objects.get(id=id)
    context = {
        'product': product
    }
    return render(request, 'myapp/detail.html', context)

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            print("yes its valid")
            form.save()
        print("hello world, its not valid")
        print(form.errors)

    else:
        form = ProductForm()
    
    context = {'form': form}
    return render(request, 'myapp/addproduct.html', context)