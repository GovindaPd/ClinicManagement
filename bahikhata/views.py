from django.conf import settings
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

import json
from datetime import datetime
from .models import BahiKhata, ProductName


User = settings.AUTH_USER_MODEL


def _save_product_names(names_csv):
    product_names = {
        product_name.strip()
        for product_name in names_csv.split(',')
        if product_name.strip()
    }
    if not product_names:
        return
    try:
        ProductName.objects.bulk_create(
            [ProductName(name=name) for name in product_names],
            ignore_conflicts=True
        )
    except Exception as e:
        # messages.error(request, f"An error occurred while saving product names: {str(e)}")
        pass


@require_http_methods(["GET"])
@login_required(login_url='login')
@permission_required(['khata.view_bahikhata'], raise_exception=True)
def bahikhata(request):
    try:
        page_number = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        messages.error(request, "Page number must be integer.")
        return redirect('index')

    records = BahiKhata.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(records, 10)
    page_obj = paginator.get_page(page_number)
    return render(request, 'bahikhata_records.html', {'records': page_obj})


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
@permission_required(['khata.add_bahikhata'], raise_exception=True)
def add_bahikhata(request):
    today_date = timezone.now().date()
    today_date_string = today_date.strftime("%Y-%m-%d")
    
    if request.method == "POST":
        try:
            user = request.user
            name = request.POST.get('name', '').strip().rstrip(',').lower()
            amount = int(request.POST.get('amount', 0))
            notes = request.POST.get('notes', '').strip()
            payment_status = request.POST.get('payment_status', 'paid').strip()
            created_at = request.POST.get('created_at')
            
            if not name or not amount:
                messages.error(request, "Bill Name and Amount are required fields.")
                return render(request, 'bahikhata_add.html', context={'today_date':today_date_string})

            if created_at:
                created_at = datetime.strptime(created_at, '%Y-%m-%d').date()
                if created_at > today_date:
                    messages.error(request, "Date can't be future date.")
                    return render(request, 'bahikhata_add.html', context={'today_date':today_date_string})
            else:
                created_at = today_date
            
            BahiKhata.objects.create(
                user=user,
                name=name,
                amount=amount,
                notes=notes,
                payment_status=payment_status,
                created_at=created_at
            )
            messages.success(request, "Record added successfully.")
            _save_product_names(name)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'bahikhata_add.html', context={'today_date':today_date_string})


@require_http_methods(["GET","POST"])
@login_required(login_url='login')
@permission_required(['khata.change_bahikhata'], raise_exception=True)
def update_bahikhata(request, id):
    try:
        user = request.user
        bill = BahiKhata.objects.get(id=id)

        if request.method == 'POST':
            name = request.POST.get('name', '').strip().lower()
            amount = int(request.POST.get('amount', 0))
            notes = request.POST.get('notes', '').strip()
            payment_status = request.POST.get('payment_status', '').strip()
            created_at = request.POST.get('created_at') or timezone.now().date()
            
            bill.name = name or bill.name
            bill.amount = amount or bill.amount
            bill.notes = notes or bill.notes
            bill.payment_status = payment_status or bill.payment_status
            bill.created_at = created_at or bill.created_at
            bill.save()

            messages.success(request, "Bill update successfully.")
            return redirect('bahikhata')
    except BahiKhata.DoesNotExist:
        messages.error(request, "Bill not found.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return render(request, 'bahikhata_edit.html', {'record':bill})


@require_http_methods(["GET"])
@login_required(login_url='login')
def product_list(request):
    data = {}
    data['data'] = list(ProductName.objects.all().values_list(flat=True))
    return JsonResponse(data)