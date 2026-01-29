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
                // Verified: Using SNYK_TOKEN_TEXT as Secret Text
                withCredentials([string(credentialsId: 'SNYK_TOKEN_TEXT', variable: 'SNYK_TOKEN')]) {
                    script {
                        def snykHome = tool 'snyk-cli'
                        echo "Running Snyk Security Scans..."
                        sh "${snykHome}/snyk test --token=${SNYK_TOKEN} --severity-threshold=high || true"
                        sh "${snykHome}/snyk iac test --token=${SNYK_TOKEN} || true"
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
                    // Trivy is lightweight and works well on 1GB RAM
                    sh "trivy image --severity CRITICAL --exit-code 0 ${imageTag}"
                }
            }
        }

        stage('Infrastructure: Terraform Plan') {
            steps {
                // Matches your exact Azure credential names
                withCredentials([
                    string(credentialsId: 'Application ID', variable: 'AZ_CLIENT_ID'),
                    string(credentialsId: 'Azure-Secrets-ID', variable: 'AZ_CLIENT_SECRET'),
                    string(credentialsId: 'Directory ID', variable: 'AZ_TENANT_ID')
                ]) {
                    script {
                        sh "terraform init"
                        sh "terraform plan"
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Essential for your small VM to prevent "Disk Full" errors
            cleanWs()
        }
    }
}
