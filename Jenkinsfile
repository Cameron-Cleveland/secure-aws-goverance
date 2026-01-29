pipeline {
    agent any

    environment {
        VM_IP = "65.52.198.39" 
        JFROG_REPO = "tf-terraform" 
        APP_NAME = "healthcare-php-app"
    }

    stages {
        stage('Git: Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Security: SCA & IaC Scan (Snyk)') {
            steps {
        // This helper specifically looks for "Snyk API Token" types
        snykContext(credentialsId: 'SNYK_TOKEN') {
            script {
                def snykHome = tool 'snyk-cli'
                sh "${snykHome}/snyk test"
            }
        }
    }
}

        stage('Build: PHP Container') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    sh "docker build -t ${imageTag} ."
                }
            }
        }

        stage('Security: Image Scan (Trivy)') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    // Trivy is already on your VM
                    sh "trivy image --severity CRITICAL --exit-code 0 ${imageTag}"
                }
            }
        }

        stage('Infrastructure: Terraform Plan') {
            steps {
                withCredentials([
                    string(credentialsId: 'Azure Application ID', variable: 'AZ_CLIENT_ID'),
                    string(credentialsId: 'Azure-Secrets-ID', variable: 'AZ_CLIENT_SECRET'),
                    string(credentialsId: 'Directory ID', variable: 'AZ_TENANT_ID')
                ]) {
                    script {
                        // This assumes your .tf files are in the repo root
                        // If they are in a folder, use dir('foldername') { ... }
                        sh "terraform init"
                        sh "terraform plan"
                    }
                }
            }
        }
    }
}
