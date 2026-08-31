from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Submission, Question, Choice, Enrollment

def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'onlinecourse/course_details_bootstrap.html', {'course': course})

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    # Extract choice IDs from submitted form
    selected_ids = [int(v) for k, v in request.POST.items() if k.startswith('choice_')]
    
    # Get or create enrollment for current user
    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
    
    # Create submission record
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(selected_ids)
    submission.save()
    
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_ids = list(submission.choices.values_list('id', flat=True))
    total_score = 0
    max_score = 0
    
    # Calculate score
    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            max_score += question.grade
            if question.is_get_score(selected_ids):
                total_score += question.grade
                
    context = {
        'course': course,
        'total_score': total_score,
        'max_score': max_score,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)