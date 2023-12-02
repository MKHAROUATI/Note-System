from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from reportlab.pdfgen import canvas
from Bing.forms import NoteForm, RegisterForm
from Bing.models import Note
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required





def index(request):
    if request.user.is_authenticated:
        note = Note.objects.all()
        return render(request, 'index.html', {"notes": note})
    else:
        return redirect('login')

def login_user(request):
    if request.method == 'POST':
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request,'You Have Been Logged In Successfully')
                return redirect('index')
            else:
                messages.error(request,'Invalid Creds')
                return redirect('login')

    else:
        return render(request, 'login.html')
    
@login_required        
def logout_user(request):
        logout(request)
        messages.success(request,'You Have Been Logged Out Successfully')
        return redirect('login')

@login_required    
def create_note(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = NoteForm(request.POST)
            if form.is_valid():
                note = form.save(commit=False)
                note.user = request.user
                note.save()
                messages.success(request, 'Note successfully created!')
                return redirect('index')
            else:
                # Display form errors in the template
                messages.error(request, 'Invalid Form')
        else:
            form = NoteForm()
        return render(request, 'note.html', {'form': form})
    else:
        messages.error(request, 'Not Authorized')
        return redirect('login')
    
@login_required    
def delete_note(request,pk):
    note = get_object_or_404(Note, id=pk)
    if note.user == request.user:
        note.delete()
        messages.success(request, 'Note successfully Deleted!')
        return redirect('index')
    else:
        messages.error(request, 'You do not have permission to delete this note.')
        return redirect('index')

         
@login_required
def edit_note(request, pk):
    note = get_object_or_404(Note, id=pk)

    # Check if the authenticated user owns the note
    if note.user == request.user:
        if request.method == 'POST':
            form = NoteForm(request.POST, instance=note)
            if form.is_valid():
                form.save()
                messages.success(request, 'Note successfully updated!')
                return redirect('index')
        else:
            form = NoteForm(instance=note)
        return render(request, 'edit_note.html', {"form": form})
    else:
        messages.error(request, 'You do not have permission to edit this note.')
        return redirect('index')
        
       

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to your desired view or URL after editing the note
    else:
        form = RegisterForm()
    return render(request, 'edit_note.html', {"form": form})

def show_users(request):
    if request.user.is_authenticated:
        heads = User.objects.all()
        return render(request, 'show_users.html', {"heads": heads})

    else:
        messages.success(request, 'Not Authorised')
        return redirect('login')
    
def edit_user(request,id_user):
    utilisateur = User.objects.get(id=id_user)
    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=utilisateur)
        if request.user.is_authenticated:
            if request.user.is_superuser:
                if form.is_valid():
                    form.save()
                    messages.success(request, 'User successfully Updated!')
                    return redirect('users')
                else:
                    messages.error(request, 'Invalid Form')
            else:
                messages.success(request, 'Not Admin')
                return redirect('index')
        else:
            messages.success(request, 'Not Authorised')
            return redirect('index')
    else:
        form = RegisterForm(instance=utilisateur)
    
    return render(request, 'edit_users.html', {"form": form,'utilisateur': utilisateur})

def delete_user(request,id_user):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            note = User.objects.get(id=id_user)
            note.delete()
            messages.success(request, 'User successfully Deleted!')
            return redirect('users')
        else:
            messages.success(request, 'Not Authorised')
            return redirect('index')
    else:
        messages.success(request, 'Not Authorised')
        return redirect('index')
    
def print_note(request, pk):
    note = get_object_or_404(Note, id=pk)
    if request.user.is_authenticated:
        if note.user == request.user:
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer)
            
            # Use correct method names for the PDF object
            pdf.drawString(100, 800, f"User: {note.user}")
            pdf.drawString(100, 780, f"Title: {note.name}")
            pdf.drawString(100, 760, f"Complete: {note.complete}")  # Use correct field name
            pdf.drawString(100, 740, f"Content: {note.description}")
            
            pdf.showPage()
            pdf.save()
            
            buffer.seek(0)
            return HttpResponse(buffer.read(), content_type="application/pdf")
        else:
            messages.success(request, 'Not Authorised')
            return redirect('index')

    else:
        return redirect('login')
    
def print_all_notes(request):
    if request.user.is_authenticated:
        # Retrieve all notes for the authenticated user
        notes = Note.objects.filter(user=request.user)

        if notes.exists():  # Check if there are any notes
            buffer = BytesIO()
            template_path = 'pdf.html'
            context = {'notes': notes}

            # Create HTML content by rendering the template
            template = get_template(template_path)
            html = template.render(context)

            # Create the PDF object using the buffer as its "file"
            pdf = pisa.CreatePDF(html, dest=buffer)

            if not pdf.err:
                # Reset buffer position to start
                buffer.seek(0)

                # Return the PDF document as a response
                response = HttpResponse(buffer.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="all_notes.pdf"'
                return response

    # Handle unauthorized access or other cases
    return HttpResponse("Unauthorized", status=401)




         
         
