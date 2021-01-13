from uuid import uuid4
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import JSONField
import uuid
from django.db.models.fields import NullBooleanField

from django.db.models.fields.related import ForeignKey


class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, is_active=True, is_staff=False, is_admin=False):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            useremail=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, useremail, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            useremail,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, useremail, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            useremail,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

# 1
class User(AbstractBaseUser):
    userid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    useremail = models.EmailField(
        max_length=100, null=False, blank=False, unique=True)
    password = models.CharField(max_length=255, null=False, blank=False)
    usertoken = models.CharField(max_length=255, null=True, blank=True)

    objects = MyUserManager()
    USERNAME_FIELD = "useremail"

    class Meta:
        db_table = '"opx"."user"'

# 2
class Gender(models.Model):
    gender_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    gender_name = models.CharField(max_length=100)
    isactive = models.IntegerField(default=1, null=False, blank=False)

    class Meta:
        db_table = '"opx"."gender"'

# 3
class Role(models.Model):
    role_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    role_name = models.CharField(max_length=50)
    role_description = models.CharField(max_length=255)
    isactive = models.IntegerField(default=1, null=False, blank=False)

    class Meta:
        db_table = '"opx"."role"'

# 4
class Permissionn(models.Model):
    perm_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    perm_codename = models.CharField(max_length=100, null=False, blank=False)
    perm_name = models.CharField(max_length=255, null=False, blank=False)
    # perm_description = models.CharField(max_length=500) borrar del diagrama - changos

    class Meta:
        db_table = '"opx"."permissionn"'

# 5
class RolePermissionn(models.Model):
    role_permissionn_id = models.AutoField(primary_key=True, editable=False)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    permissionn = models.ForeignKey(Permissionn, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."role_permissionn"'

# 6
class City(models.Model):
    city_id = models.CharField(primary_key=True, editable=False, max_length=50)
    city_name = models.CharField(max_length=100)

    class Meta:
        db_table = '"opx"."city"'

# 7
class Neighborhood(models.Model):
    neighb_id = models.IntegerField(primary_key=True, editable=False)
    neighb_name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."neighborhood"'

# 8
class EducationLevel(models.Model):
    educlevel_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    educlevel_name = models.CharField(max_length=100)
    isactive = models.IntegerField(default=1, null=False, blank=False)

    class Meta:
        db_table = '"opx"."education_level"'

# 9 preguntar MSedan sobre conflictividades
class Person(models.Model):
    pers_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    pers_name = models.CharField(max_length=255, null=False, blank=False)
    pers_lastname = models.CharField(max_length=255, null=False, blank=False)
    pers_birthdate = models.DateField(null=False, blank=False)
    pers_telephone = models.CharField(max_length=20)
    pers_latitude = models.CharField(blank=True, null=True, max_length=30)
    pers_longitude = models.CharField(blank=True, null=True, max_length=30)
    hour_location = models.CharField(blank=True, null=True, max_length=100)
    pers_score = models.IntegerField(null=True, blank=True, default=0)
    pers_creation_date = models.DateTimeField(auto_now_add=True, blank=True)
    #fcm_token = models.CharField(max_length=255, null=True, blank=True)
    isactive = models.IntegerField(default=1, null=False, blank=False)
    isemployee = models.IntegerField(default=0, null=False, blank=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.PROTECT)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.PROTECT)
    education_level = models.ForeignKey(
        EducationLevel, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."person"'

# 10
class ProjectType(models.Model):
    projtype_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    projtype_name = models.CharField(max_length=100)
    projtype_description = models.CharField(max_length=500)

    class Meta:
        db_table = '"opx"."project_type"'

#11
class Project(models.Model):
    proj_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    proj_name = models.CharField(max_length=100, unique=True)
    proj_description = models.CharField(max_length=500)
    proj_external_id = models.CharField(max_length=500)  # Revisar esta columna
    proj_creation_date = models.DateTimeField(auto_now_add=True, blank=True)
    proj_close_date = models.DateField(null=True, blank=True)
    proj_start_date = models.DateField(null=True, blank=True)
    proj_completness = models.FloatField(default=0.0)
    isactive = models.IntegerField(default=1, null=False, blank=False)
    project_type = models.ForeignKey(ProjectType, on_delete=models.PROTECT)
    proj_owner = models.ForeignKey(Person, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."project"'

# 12
class DimensionType(models.Model):
    dim_type_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    dim_type_name = models.CharField(max_length=100, null=False, blank=False)
    dim_type_description = models.CharField(
        max_length=300, null=True, blank=True)

    class Meta:
        db_table = '"opx"."dimension_type"'

# 13
class TerritorialDimension(models.Model):
    dimension_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    dimension_name = models.CharField(max_length=100, unique=True)
    dimension_geojson = JSONField()
    neighborhood_id = models.CharField(max_length=100, null=True, blank=True)
    isactive = models.IntegerField(default=1, null=False, blank=False)
    preloaded = models.IntegerField(default=0, null=False, blank=False)
    dimension_type = models.ForeignKey(DimensionType, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."territorial_dimension"'

# 14
class ProjectTerritorialDimension(models.Model):
    proj_dimension_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    territorial_dimension = models.ForeignKey(
        TerritorialDimension, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."project_dimension"'

# 15
class Decision(models.Model):
    decs_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    decs_name = models.CharField(max_length=100, unique=True)
    decs_description = models.CharField(max_length=500)

    class Meta:
        db_table = '"opx"."decision"'

# 16
class ProjectDecision(models.Model):
    proj_decs_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    decision = models.ForeignKey(Decision, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."project_decision"'

# 17
class Team(models.Model):
    team_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    team_name = models.CharField(max_length=100, unique=True)
    team_description = models.CharField(max_length=300, unique=True)
    team_leader = models.ForeignKey(Person, on_delete=models.PROTECT)
    team_effectiveness = models.FloatField(default=0.0)  # agreagr al diagrama - changos

    class Meta:
        db_table = '"opx"."team"'

# 18
class TeamPerson(models.Model):
    teampers_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    participation = models.FloatField(default=0)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."team_person"'

# 19
class ProjectTeam(models.Model):
    proj_team_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."project_team"'

# 20
class Context(models.Model):
    context_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    context_description = models.CharField(max_length=500)

    class Meta:
        db_table = '"opx"."context"'

# 21
class DataContext(models.Model):
    data_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    hdxtag = models.CharField(max_length=100)
    data_value = models.CharField(max_length=100)
    data_type = models.CharField(max_length=100)
    data_description = models.CharField(max_length=500)
    data_geojson = JSONField()
    data_date = models.DateField(null=True, blank=True)
    data_time = models.TimeField(null=True, blank=True)
    context = models.ForeignKey(Context, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."data_context"'

# 22
class ProjectContext(models.Model):
    proj_context_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    context = models.ForeignKey(Context, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."project_context"'

# 23
class TaskPriority(models.Model):
    priority_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    priority_name = models.CharField(max_length=100)
    priority_number = models.IntegerField(default=0)

    class Meta:
        db_table = '"opx"."task_priority"'

# 24
class TaskType(models.Model):
    task_type_id = models.AutoField(
        primary_key=True, editable=False)
    task_type_name = models.CharField(max_length=100)
    task_type_description = models.CharField(max_length=300)

    class Meta:
        db_table = '"opx"."task_type"'

# 25
class TaskRestriction(models.Model):
    restriction_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    task_start_date = models.DateField(null=True, blank=True)
    task_end_date = models.DateField(null=True, blank=True)
    # task = models.ForeignKey(Task, on_delete=models.PROTECT) # borrar del Diagram - changos

    class Meta:
        db_table = '"opx"."task_restriction"'

# 26
class Instrument(models.Model):
    instrument_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    external_id = models.CharField(max_length=255)
    instrument_type = models.IntegerField()  # 1 KoboInstrument; 2 TM instrument
    instrument_name = models.CharField(max_length=100)
    instrument_description = models.CharField(max_length=300)
    geojson = JSONField(blank=True, null=True)

    class Meta:
        db_table = '"opx"."instrument"'

# 27
class Task(models.Model):
    task_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    task_name = models.CharField(max_length=100, unique=True)
    task_description = models.CharField(max_length=300)
    task_observation = models.CharField(max_length=1000)
    task_creation_date = models.DateTimeField(auto_now_add=True, blank=True)
    task_quantity = models.IntegerField(default=0, null=False, blank=False)
    task_completness = models.FloatField(default=0)
    isactive = models.IntegerField(default=1, null=False, blank=False)
    task_priority = models.ForeignKey(TaskPriority, on_delete=models.PROTECT)
    task_type = models.ForeignKey(TaskType, on_delete=models.PROTECT)
    proj_dimension = models.ForeignKey(
        TerritorialDimension, related_name='proj_dimension',on_delete=models.PROTECT)
    territorial_dimension = models.ForeignKey(
        TerritorialDimension, related_name='territorial_dimension',on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    task_restriction = models.OneToOneField(
        TaskRestriction, on_delete=models.PROTECT)  # agregar al Diag - changos
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."task"'

# 28
class PersonTask(models.Model):
    person_task_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    score = models.IntegerField(null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    task = models.ForeignKey(Task, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."person_task"'

# 29
class Params(models.Model):
    params_id = models.CharField(
        primary_key=True, editable=False, max_length=500)
    params_value = models.CharField(max_length=500)
    params_description = models.CharField(max_length=500)

    class Meta:
        db_table = '"opx"."params"'

# 30
class PeaceInitiative(models.Model):
    peace_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    peace_name = models.CharField(max_length=100)
    peace_description = models.CharField(max_length=500)
    peace_geojson = JSONField()
    peace_start_date = models.DateField()
    peace_end_date = models.DateField(null=True, blank=True)
    peace_tag = models.CharField(max_length=50)
    osm_icon_tag = models.CharField(max_length=30)
    isvalid = models.IntegerField(null=True, blank=True)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."peace_initiative"'

# 31
class PeaceSchedule(models.Model):
    peace_shc_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    peace_shc_day = models.CharField(max_length=50)
    peace_shc_time = models.TimeField(null=True, blank=True)
    peace_initiative = models.ForeignKey(
        PeaceInitiative, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."peace_schedule"'

# 32
class Comment(models.Model):
    comment_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    comment_title = models.CharField(max_length=100)
    comment_description = models.CharField(max_length=500)
    comment_date = models.DateTimeField(auto_now_add=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."comment"'

# 33
class Conflict(models.Model):
    conflict_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    conflict_name = models.CharField(max_length=50)

    class Meta:
        db_table = '"opx"."conflict"'

# 34
class Contextualization(models.Model):
    contxzn_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    fact_date = models.DateField()
    fact_hour = models.TimeField()
    fac_day = models.IntegerField()
    fact_age = models.IntegerField()
    #nombre_barrio = models.CharField(max_length=300) como ya está el barrio no es necesario
    contxzn_quantity = models.IntegerField(null=True)
    education_level = models.ForeignKey(
        EducationLevel, on_delete=models.PROTECT, null=True, blank=True)
    gender = models.ForeignKey(
        Gender, on_delete=models.PROTECT, null=True, blank=True)
    neighborhood = models.ForeignKey(
        Neighborhood, on_delete=models.PROTECT, null=True, blank=True)
    conflict = models.ForeignKey(Conflict, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."contextualization"'


# 35 Corregir en el Diag
class Survery(models.Model):
    survery_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    koboid = models.CharField(max_length=255, null=False, blank=True)
    survery_content = JSONField()
    survery_state = models.IntegerField(default=0) #revisar el default
    survery_observation = models.CharField(max_length=1000, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."survery"'

# 36
class OsmElement(models.Model):
    osmelement_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    osmelement_name = models.CharField(max_length=255)
    osm_key = models.CharField(max_length=255)
    osm_value = models.CharField(max_length=255)
    closed_way = models.IntegerField()

    class Meta:
        db_table = '"opx"."osm_element"'

# 37
class Cartography(models.Model):
    cartography_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False)
    osmid = models.CharField(max_length=100)
    cartography_state = models.IntegerField(default=1)
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    osm_elemtent = models.ForeignKey(OsmElement, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."cartography"'

#38
class Notification(models.Model):
    notification_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    notification_type = models.IntegerField()
    description = JSONField()
    project_name = models.CharField(max_length=100, null=True, blank=True)
    task_name = models.CharField(max_length=100, null=True, blank=True)
    notification_date = models.DateTimeField(auto_now_add=True)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

    class Meta:
        db_table = '"opx"."notification"'
        