from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model, authenticate, login
from neo4j import GraphDatabase
from django.contrib.auth.hashers import make_password
from .models import Neo4jUser
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required

User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            hashed_password = make_password(password)

            Neo4jUser.create_user(username, hashed_password, email)

            User.objects.create_user(username=username, password=password, email=email)

            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'app/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('recommend')
            else:
                form.add_error('password', 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'app/login.html', {'form': form})


def trending_products(request):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))

    cypher_query = """
    MATCH (p:Product)
    OPTIONAL MATCH (p)<-[v:VIEWS]-()
    OPTIONAL MATCH (p)<-[l:LIKES]-()
    WITH p, COUNT(v) AS viewCount, COUNT(l) AS likeCount
    RETURN p, (viewCount * 1 + likeCount * 2) AS popularityScore
    ORDER BY popularityScore DESC
    LIMIT 24
    """

    with driver.session() as session:
        result = session.run(cypher_query)
        products = [record['p'] for record in result]

    driver.close()

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'app/home.html', {'products': products})


@login_required
def apple_products(request):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))

    cypher_query = """
    MATCH (p:Product {brand_name: 'apple'})
    RETURN p
    """

    with driver.session() as session:
        result = session.run(cypher_query)
        products = [record['p'] for record in result]

    driver.close()

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'app/apple.html', {'products': products})


@login_required
def samsung_products(request):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))

    cypher_query = """
    MATCH (p:Product {brand_name: 'samsung'})
    RETURN p
    """

    with driver.session() as session:
        result = session.run(cypher_query)
        products = [record['p'] for record in result]

    driver.close()

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'app/samsung.html', {'products': products})


@login_required
def xiaomi_products(request):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))

    cypher_query = """
    MATCH (p:Product {brand_name: 'xiaomi'})
    RETURN p
    """

    with driver.session() as session:
        result = session.run(cypher_query)
        products = [record['p'] for record in result]

    driver.close()

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'app/xiaomi.html', {'products': products})


@login_required
def product_details(request, model):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))

    username = request.user.username

    cypher_query = f"""
        MERGE (u:User {{username: '{username}'}})
        MERGE (p:Product {{model: '{model}'}})
        MERGE (u)-[:VIEWS]->(p)
        RETURN p
    """

    with driver.session() as session:
        result = session.run(cypher_query)
        products = [record['p'] for record in result]

    driver.close()

    return render(request, 'app/product_detail.html', {'product': products[0]})


@login_required
def recommended_products(request):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))

    username = request.user.username

    cypher_query = f"""
        MATCH (targetUser:User {{username: '{username}'}})
        WITH targetUser

        MATCH (targetUser)-[:VIEWS|LIKES]->()<-[:VIEWS|LIKES]-(similarUser:User)-[:VIEWS|LIKES]->(product:Product)
        WHERE targetUser <> similarUser

        WITH targetUser, product, COUNT(DISTINCT similarUser) AS similarityScore
        ORDER BY similarityScore DESC
        LIMIT 12

        RETURN COLLECT(product) AS recommendedProducts
    """

    with driver.session() as session:
        result = session.run(cypher_query)
        products = result.single()['recommendedProducts']

    driver.close()

    return render(request, 'app/recommend.html', {'products': products})



@login_required
def search(request):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))

    prompt = request.GET.get('q', '').lower()

    cypher_query = f"""
           MATCH (p:Product)
           WHERE toLower(p.model) CONTAINS toLower('{prompt}')
           RETURN p
       """

    with driver.session() as session:
        result = session.run(cypher_query)
        products = [record['p'] for record in result]

    driver.close()

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'app/search.html', {'products': products, 'query': prompt})


@login_required
def like_product(request, model):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "adminadmin"))

    username = request.user.username

    cypher_query = f"""
            MERGE (u:User {{username: '{username}'}})
            MERGE (p:Product {{model: '{model}'}})
            MERGE (u)-[:LIKES]->(p)
        """

    with driver.session() as session:
        session.run(cypher_query)

    return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))
