from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages

from .forms import EmployerOrganizationForm, JobPostingForm

from django.http import HttpResponse

from .models import EmployerOrganization, JobPosting #have to pull from the models to list them all
from core.models import UserProfile
from job_applications.models import JobApplication  # Adjust the import path according to your project structure

from django.urls import reverse
from django.utils import timezone


def index(request):
    return HttpResponse("Job Catalog app section")

def display_all_companies(request):  #not sure where "request" comes from
    all_organizations = EmployerOrganization.objects.all()
    context = {'organizations_list': all_organizations}  # we are declaring, not pulling variables here
    return render(request, 'job_catalog/all_companies.html' ,context)  #the 2nd argument auto-requested a template_name, and it will default to the templates folder as the root



def display_all_jobs(request):
    all_jobs = JobPosting.objects.all()
    context = {'job_postings_list': all_jobs}  # we are declaring, not pulling variables here
    return render(request, 'job_catalog/all_jobs.html' ,context)


def job_details(request, job_id):
    job_instance = get_object_or_404(JobPosting, pk=job_id)
    user_has_applied = False
    application = None

    if request.user.is_authenticated:
        try:
            application = JobApplication.objects.get(job_posting=job_instance, user=request.user)
            user_has_applied = True
        except JobApplication.DoesNotExist:
            user_has_applied = False

    context = {
        'job_instance': job_instance,
        'user_has_applied': user_has_applied,
        'application': application,  # Optional: Only if you need more details from the application itself
    }
    return render(request, 'job_catalog/job_details.html', context)

def company_details(request, company_id):
    company_instance = get_object_or_404(EmployerOrganization, pk=company_id)
    total_job_postings = JobPosting.objects.filter(organization=company_instance).count()
    active_job_postings = JobPosting.objects.filter(organization=company_instance, is_active=True).count()
    job_postings = JobPosting.objects.filter(organization=company_instance, is_active=True)

    context = {
        'company_instance': company_instance,
        'job_postings': job_postings,
        'total_job_postings': total_job_postings,  # Total number of jobs posted
        'active_job_postings': active_job_postings,  # Number of active jobs
    }
    return render(request, 'job_catalog/company_details.html', context)


def create_organization(request):
    # Check if the user is logged in and doesn't already belong to an organization
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create an organization.")
        return redirect('core:login_start')

    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile.organization:
        org_name = user_profile.organization.employer_org_name
        messages.error(request,
                       f"You cannot create a company since you are currently representing {org_name} for hiring.")
        return redirect('job_catalog:index')  # Adjust as needed

    if request.method == 'POST':
        form = EmployerOrganizationForm(request.POST)
        if form.is_valid():
            new_organization = form.save()
            user_profile.organization = new_organization
            user_profile.save()
            messages.success(request, "Organization created successfully.")
            return redirect('job_catalog:index')  # Redirect to an appropriate page
    else:
        form = EmployerOrganizationForm()

    return render(request, 'job_catalog/create_organization_form.html', {'form': form})

def create_job_posting(request):
    print("Entered create_job_posting view")
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to post a job.")
        return redirect('core:login_start')

    if not hasattr(request.user, 'profile') or not request.user.profile.organization:
        messages.error(request, "You need to be associated with an organization to post a job.")
        return redirect('/')  # Redirect to the home page if not associated with an organization

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        print("Form created")
        if form.is_valid():
            print("Form is valid")
            job_posting = form.save(commit=False)
            job_posting.organization = request.user.profile.organization  # Associate the job posting with the organization
            # Set the post date to now and calculate the expiration date
            job_posting.post_date = timezone.now()
            job_posting.expiration_date = timezone.now() + timezone.timedelta(days=90)
            job_posting.save()
            print(f"Job Posting created with ID: {job_posting.id}")
            messages.success(request, 'Job posting created successfully.')
            return redirect(reverse('job_catalog:job_details', args=[job_posting.id]))
        else:
            # This block will execute if form is not valid
            print("Form is not valid")
            print(form.errors)
    else:
        form = JobPostingForm()

    return render(request, 'job_catalog/create_job_posting.html', {'form': form})