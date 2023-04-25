from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from .models import Product, OrderDetail
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from django.http.response import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import stripe


# Create your views here.
def index(request):
    return HttpResponse("hello world")

def products(request):
    products = Product.objects.all()
    product_name = request.GET.get('product_name')
    if product_name:
        page_obj = products.filter(name__icontains=product_name)
    else:
        page_obj = products
    paginator = Paginator(page_obj, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'products': page_obj,
        'page_obj': page_obj
    }
    return render(request, "myapp/index.html", context)

# class based view for above products view [ListView]
class ProductsListView(ListView):
    model = Product
    template_name = 'myapp/index.html'
    context_object_name = 'products'
    paginate_by = 3

# def product_detail(request, id):
#     product = Product.objects.get(id=id)
#     context = {
#         'product': product
#     }
#     return render(request, 'myapp/detail.html', context)

#Class based view for above product detail view
class ProductDetailView(DetailView):
    model = Product
    template_name = 'myapp/detail.html'
    context_object_name = 'product'
    pk_url_kwarg='pk'
    
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context

# @login_required
# def add_product(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             print("yes its valid")
#             form_model = form.save(commit=False)
#             form_model.seller_name = request.user
#             form_model.save()
#     else:
#         form = ProductForm()
    
#     context = {'form': form}
#     return render(request, 'myapp/addproduct.html', context)

# class based view for creating a product
class ContactFormView(LoginRequiredMixin, FormView):
    template_name = "myapp/addproduct.html"
    form_class = ProductForm
    success_url = "myapp/add_product/"

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form_model = form.save(commit=False)
        form_model.seller_name = self.request.user
        return super().form_valid(form)


@login_required
def my_listings(request):
    products = Product.objects.filter(seller_name=request.user)
    context = {
        'products': products
    }
    return render(request, 'myapp/mylistings.html', context)

def update_product(request, id):
    pass

def delete_product(request, id):
    pass


@csrf_exempt
def create_checkout_session(request, id):
    product = get_object_or_404(Product, pk=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        customer_email = request.user.email,
        payment_method_types = ['card'],
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': 1,
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse('myapp:success'))+"?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_uri(reverse('myapp:failed')),
    )

    order = OrderDetail()
    order.customer_username = request.user.username
    order.product = product
    order.stripe_payment_intent = checkout_session['id']
    order.amount = int(product.price * 100)
    order.save()
    return JsonResponse({'sessionId': checkout_session.id})


class PaymentSuccessView(TemplateView):
    template_name = 'myapp/payment_success.html'

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if session_id is None:
            return HttpResponseNotFound()
        session = stripe.checkout.Session.retrieve(session_id)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        order = get_object_or_404(OrderDetail, stripe_payment_intent=session.id)
        order.has_paid = True
        order.save()
        return render(request, self.template_name)
    
class PaymentFailedView(TemplateView):
    template_name = 'myapp/payment_failed.html'