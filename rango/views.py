from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse 
from django.urls import reverse
from datetime import datetime
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val

    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, "visits", "1"))
    last_visit_cookie = get_server_side_cookie(request, "last_visit", str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session["last_visit"] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session["last_visit"] = last_visit_cookie

    # Update/set the visits cookie
    request.session["visits"] = visits

def index(request):
    category_list = Category.objects.order_by("-likes")[:5]
    page_list = Page.objects.order_by("-views")[:5]

    context_dict = {}
    context_dict["boldmessage"] = "Crunchy, creamy, cookie, candy, cupcake!"
    context_dict["categories"] = category_list
    context_dict["pages"] = page_list

    visitor_cookie_handler(request)

    # request.session.set_test_cookie()
    response  = render(request, "rango/index.html", context=context_dict)
    return response


def about(request):
    context_dict = {"boldmessage": "This tutorial has been put together by freddie nelson."}

    visitor_cookie_handler(request)
    context_dict["visits"] = request.session["visits"]
    
    # if request.session.test_cookie_worked():
    #     print("TEST COOKIE WORKED!")
    #     request.session.delete_test_cookie()

    return render(request, "rango/about.html", context=context_dict)

def show_category(request, category_name_slug):
    context_dict = {}
    
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)

        context_dict["pages"] = pages
        context_dict["category"] = category

    except Category.DoesNotExist:
        context_dict["category"] = None
        context_dict["pages"] = None

    return render(request, "rango/category.html", context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return redirect("/rango/")
        else:
            print(form.errors)
    
    return render(request, "rango/add_category.html", {"form": form})

@login_required
def add_page(request, category_name_slug):
    context_dict = {}

    try:
        context_dict["category"] = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        context_dict["category"] = None
    
    if context_dict["category"] == None:
        return redirect("/rango/")
    
    form = PageForm()
    
    if request.method == "POST": 
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)
            page.category = context_dict["category"]
            page.views = 0
            page.save()

            return redirect(reverse("rango:show_category", kwargs={"category_name_slug": category_name_slug}))
        else:
            print(form.errors)
    
    context_dict["form"] = form
        
    return render(request, "rango/add_page.html", context=context_dict)


def register(request):
    registered = False

    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # hashes the password
            user.set_password(user.password)

            # saves the user to the db
            user.save()

            # create profile but don't commit change to db
            # avoids integrity problems as not linked to user yet
            profile = profile_form.save(commit=False)
            profile.user = user

            if "picture" in request.FILES:
                profile.picture = request.FILES["picture"]

            profile.save()

            registered = True
        
        else:
            # failed
            print(user_form.errors, profile_form.errors)
        
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context = {"user_form": user_form, "profile_form": profile_form, "registered": registered}

    return render(request, "rango/register.html", context=context)


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == "POST":
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse("rango:index"))

            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")

        else:
            # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, "rango/login.html")


def user_logout(request):
    logout(request)
    return redirect(reverse("rango:index"))

@login_required
def restricted(request):
    return render(request, "rango/restricted.html")

