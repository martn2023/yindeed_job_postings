from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from collections import defaultdict
from .forms import JobApplicationForm
from .models import JobPosting, JobApplication


def apply_for_job(request, job_posting_id):
    job_posting = get_object_or_404(JobPosting, pk=job_posting_id)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Check for an existing application
            existing_application = JobApplication.objects.filter(
                user=request.user,
                job_posting=job_posting
            ).exists()

            if existing_application:
                # User has already applied
                messages.error(request, "You have already applied for this job.")
                return redirect('job_applications:apply_for_job', job_posting_id=job_posting_id)

            application = form.save(commit=False)
            application.user = request.user
            application.job_posting = job_posting
            application.save()
            return redirect('job_applications:application_accepted', application_id=application.id)
        else:
            # Form is not valid, show the form again with errors
            context = {
                'form': form,
                'job_posting': job_posting
            }
            return render(request, 'job_applications/apply_for_job.html', context)
    else:
        form = JobApplicationForm(initial={'job_posting': job_posting_id, 'user': request.user.id})

    context = {
        'form': form,
        'job_posting': job_posting
    }
    return render(request, 'job_applications/apply_for_job.html', context)


def application_accepted(request, application_id):
    application = get_object_or_404(JobApplication, pk=application_id)
    return render(request, 'job_applications/application_accepted.html', {'application': application})


def my_job_applications(request):
    if not request.user.is_authenticated:
        # Redirect to login page
        return redirect(reverse('core:login_start'))

    job_applications = JobApplication.objects.filter(user=request.user).select_related(
        'job_posting__organization').order_by('-submit_date')
    applications_grouped = defaultdict(list)
    for job_app in job_applications:
        applications_grouped[job_app.job_posting.organization].append(job_app)

    context = {
        'applications_grouped': dict(applications_grouped)
    }
    return render(request, 'job_applications/users_job_applications.html', context)


def view_applications_for_employer(request):
    if not request.user.is_authenticated:
        return redirect('core:login_start')  # Redirect unauthenticated users to login page

    # Assuming the User model has a one-to-one link to a UserProfile model, which in turn is linked to an EmployerOrganization.
    if hasattr(request.user, 'userprofile') and request.user.userprofile.organization:
        employer_org = request.user.userprofile.organization
        job_postings = JobPosting.objects.filter(organization=employer_org)
        job_applications = JobApplication.objects.filter(job_posting__in=job_postings).select_related('user').order_by('-submit_date')

        applications_grouped_by_job = defaultdict(list)
        for application in job_applications:
            applications_grouped_by_job[application.job_posting].append(application)

        context = {
            'applications_grouped_by_job': dict(applications_grouped_by_job),
            'employer_org': employer_org,  # you can pass the organization to the template if needed
        }
        return render(request, 'job_applications/employer_applications.html', context)
    else:
        # If the user is not linked to any organization or not an employer
        # You can choose to redirect them or simply show an error page
        return render(request, 'job_applications/unauthorized.html')  # Make sure to create this template or handle accordingly
