from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
import os

#Perfil de usuario, sirve para editar el perfil y la parte del inventario
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

    def delete_profile_picture(self):
        if self.profile_picture and os.path.isfile(self.profile_picture.path):
            os.remove(self.profile_picture.path)
            self.profile_picture.delete(save=False)

# Tabla para manejar los usuarios agregados por el admin
# Esta tabla se utiliza para gestionar los usuarios aprobados por el administrador.
class ApprovedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Usuario creado
    date_approved = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="approved_by")  # Admin que lo creó

    def __str__(self):
        return f"{self.user.username} (Creado por: {self.created_by.username if self.created_by else 'Desconocido'})"
    