from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, LawyerProfile, UserProfile, Appointment, LawyerRating, CaseFile, ChatMessage
from django.core.mail import send_mail
from django.conf import settings


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    user_type = forms.ChoiceField(
        choices=[('user', 'User'), ('lawyer', 'Lawyer')],
        widget=forms.RadioSelect,
        required=True
    )
    
    photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'user_type', 'photo')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
            # Create profile based on user type
            if user.user_type == 'lawyer':
                profile = LawyerProfile.objects.create(user=user)
                photo = self.files.get('photo')
                if photo:
                    profile.photo = photo
                    profile.save()
            elif user.user_type == 'user':
                profile = UserProfile.objects.create(user=user)
                photo = self.files.get('photo')
                if photo:
                    profile.photo = photo
                    profile.save()
        return user


class LawyerProfileForm(forms.ModelForm):
    class Meta:
        model = LawyerProfile
        fields = ['lawyer_type', 'bio', 'experience_years', 'phone_number', 'address', 'photo']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'date_of_birth', 'photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'message', 'consultation_type']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'message': forms.Textarea(attrs={'rows': 4}),
            'consultation_type': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        from django.utils import timezone
        self.fields['appointment_date'].widget.attrs['min'] = timezone.now().date().isoformat()


class LawyerRatingForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)], widget=forms.RadioSelect)

    class Meta:
        model = LawyerRating
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=150)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))

    def send(self):
        send_mail(
            f"[Contact] {self.cleaned_data['subject']}",
            f"From: {self.cleaned_data['name']} <{self.cleaned_data['email']}>)\n\n{self.cleaned_data['message']}",
            settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )


class CaseFileForm(forms.ModelForm):
    class Meta:
        model = CaseFile
        fields = ['file', 'file_type', 'description']
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        file_type = self.cleaned_data.get('file_type')
        
        if file:
            # Get file extension and check against file type
            file_extension = file.name.split('.')[-1].lower()
            
            if file_type == 'image' and file_extension not in ['jpg', 'jpeg', 'png', 'gif']:
                raise forms.ValidationError('Invalid image file format. Please upload JPG, PNG or GIF.')
            elif file_type == 'pdf' and file_extension != 'pdf':
                raise forms.ValidationError('Invalid file format. Please upload a PDF file.')
            elif file_type == 'video' and file_extension not in ['mp4', 'mov', 'avi']:
                raise forms.ValidationError('Invalid video format. Please upload MP4, MOV or AVI.')
            
            # Check file size (limit to 50MB)
            if file.size > 50 * 1024 * 1024:  # 50MB in bytes
                raise forms.ValidationError('File size cannot exceed 50MB.')
                
        return file


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'attachment']

