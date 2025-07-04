from django.shortcuts import render, redirect
from .models import Expense, Category
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

def add_expense(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        amount = request.POST['amount']
        date = request.POST['date']
        category_id = request.POST['category']
        description = request.POST['description']

        category = Category.objects.get(id=category_id)

        Expense.objects.create(
            amount=amount,
            date=date,
            category=category,
            description=description
        )
        return redirect('expense_list')

    return render(request, 'expenses/add_expense.html', {'categories': categories})
def edit_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        expense.amount = request.POST['amount']
        expense.date = request.POST['date']
        category_id = request.POST['category']
        expense.category = Category.objects.get(id=category_id)
        expense.description = request.POST['description']
        expense.save()
        return redirect('expense_list')

    return render(request, 'expenses/edit_expense.html', {'expense': expense, 'categories': categories})


def delete_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id)
    expense.delete()
    return redirect('expense_list')

def dashboard(request):
    # Expenses per category
    category_data = Expense.objects.values('category__name').annotate(total=Sum('amount'))
    categories = [item['category__name'] for item in category_data]
    category_totals = [float(item['total']) for item in category_data]

    # Expenses per month
    monthly_data = Expense.objects.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
    months = [item['month'].strftime("%Y-%m") for item in monthly_data]
    monthly_totals = [float(item['total']) for item in monthly_data]

    # Total spent this month
    now = timezone.now()
    this_month_total = Expense.objects.filter(date__month=now.month, date__year=now.year).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'expenses/dashboard.html', {
        'categories': categories,
        'category_totals': category_totals,
        'months': months,
        'monthly_totals': monthly_totals,
        'this_month_total': float(this_month_total)
    })
def export_csv(request):
    # Create HTTP response with CSV mimetype
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount', 'Description'])

    expenses = Expense.objects.all()
    for exp in expenses:
        writer.writerow([exp.date, exp.category.name, exp.amount, exp.description])

    return response
@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses/expense_list.html', {'expenses': expenses})

@login_required
def add_expense(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        amount = request.POST['amount']
        date = request.POST['date']
        category_id = request.POST['category']
        description = request.POST['description']
        category = Category.objects.get(id=category_id)
        Expense.objects.create(
            user=request.user,
            category=category,
            amount=amount,
            date=date,
            description=description
        )
        return redirect('expense_list')
    return render(request, 'expenses/add_expense.html', {'categories': categories})

@login_required
def edit_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id, user=request.user)
    categories = Category.objects.all()
    if request.method == 'POST':
        expense.amount = request.POST['amount']
        expense.date = request.POST['date']
        category_id = request.POST['category']
        expense.category = Category.objects.get(id=category_id)
        expense.description = request.POST['description']
        expense.save()
        return redirect('expense_list')
    return render(request, 'expenses/edit_expense.html', {'expense': expense, 'categories': categories})

@login_required
def delete_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id, user=request.user)
    expense.delete()
    return redirect('expense_list')

@login_required
def dashboard(request):
    # Filter data only for this user
    category_data = Expense.objects.filter(user=request.user).values('category__name').annotate(total=Sum('amount'))
    categories = [item['category__name'] for item in category_data]
    category_totals = [float(item['total']) for item in category_data]

    monthly_data = Expense.objects.filter(user=request.user).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
    months = [item['month'].strftime("%Y-%m") for item in monthly_data]
    monthly_totals = [float(item['total']) for item in monthly_data]

    now = timezone.now()
    this_month_total = Expense.objects.filter(user=request.user, date__month=now.month, date__year=now.year).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'expenses/dashboard.html', {
        'categories': categories,
        'category_totals': category_totals,
        'months': months,
        'monthly_totals': monthly_totals,
        'this_month_total': float(this_month_total)
    })

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount', 'Description'])
    expenses = Expense.objects.filter(user=request.user)
    for exp in expenses:
        writer.writerow([exp.date, exp.category.name, exp.amount, exp.description])
    return response
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'expenses/register.html', {'form': form})
