{{/*
Expand the name of the chart.
*/}}
{{- define "sagemcp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "sagemcp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "sagemcp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "sagemcp.labels" -}}
helm.sh/chart: {{ include "sagemcp.chart" . }}
{{ include "sagemcp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "sagemcp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sagemcp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "sagemcp.backend.labels" -}}
{{ include "sagemcp.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "sagemcp.backend.selectorLabels" -}}
{{ include "sagemcp.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "sagemcp.frontend.labels" -}}
{{ include "sagemcp.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "sagemcp.frontend.selectorLabels" -}}
{{ include "sagemcp.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "sagemcp.serviceAccountName" -}}
{{- if .Values.backend.serviceAccount.create }}
{{- default (include "sagemcp.fullname" .) .Values.backend.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.backend.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
PostgreSQL host
*/}}
{{- define "sagemcp.postgresql.host" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" .Release.Name }}
{{- else }}
{{- .Values.externalDatabase.host }}
{{- end }}
{{- end }}

{{/*
PostgreSQL port
*/}}
{{- define "sagemcp.postgresql.port" -}}
{{- if .Values.postgresql.enabled }}
{{- 5432 }}
{{- else }}
{{- .Values.externalDatabase.port }}
{{- end }}
{{- end }}

{{/*
PostgreSQL username
*/}}
{{- define "sagemcp.postgresql.username" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.username }}
{{- else }}
{{- .Values.externalDatabase.username }}
{{- end }}
{{- end }}

{{/*
PostgreSQL password secret name
*/}}
{{- define "sagemcp.postgresql.secretName" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" .Release.Name }}
{{- else }}
{{- printf "%s-external-db" (include "sagemcp.fullname" .) }}
{{- end }}
{{- end }}

{{/*
PostgreSQL database
*/}}
{{- define "sagemcp.postgresql.database" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.database }}
{{- end }}
{{- end }}

{{/*
PostgreSQL connection string
*/}}
{{- define "sagemcp.postgresql.connectionString" -}}
{{- printf "postgresql://%s:$(POSTGRES_PASSWORD)@%s:%v/%s" (include "sagemcp.postgresql.username" .) (include "sagemcp.postgresql.host" .) (include "sagemcp.postgresql.port" .) (include "sagemcp.postgresql.database" .) }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "sagemcp.redis.host" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" .Release.Name }}
{{- else }}
{{- .Values.externalRedis.host }}
{{- end }}
{{- end }}

{{/*
Redis port
*/}}
{{- define "sagemcp.redis.port" -}}
{{- if .Values.redis.enabled }}
{{- 6379 }}
{{- else }}
{{- .Values.externalRedis.port }}
{{- end }}
{{- end }}

{{/*
Redis password secret name
*/}}
{{- define "sagemcp.redis.secretName" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis" .Release.Name }}
{{- else }}
{{- printf "%s-external-redis" (include "sagemcp.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Redis connection string
*/}}
{{- define "sagemcp.redis.connectionString" -}}
{{- if .Values.redis.enabled }}
{{- printf "redis://:%s@%s:%v/0" "$(REDIS_PASSWORD)" (include "sagemcp.redis.host" .) (include "sagemcp.redis.port" .) }}
{{- else }}
{{- printf "redis://:%s@%s:%v/%v" "$(REDIS_PASSWORD)" (include "sagemcp.redis.host" .) (include "sagemcp.redis.port" .) .Values.externalRedis.database }}
{{- end }}
{{- end }}
