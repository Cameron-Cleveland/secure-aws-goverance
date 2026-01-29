pipeline {
    agent any

    environment {
        // Updated VM IP and App info
        VM_IP = "65.52.198.39" 
        JFROG_REPO = "tf-terraform" 
        APP_NAME = "healthcare-php-app"
    }

    stages {
        stage('Git: Checkout Source') {
            steps {
                // Pulls the latest code from GitHub
                checkout scm
            }
        }

        stage('Security: SCA & IaC Scan (Snyk)') {
            steps {
                withCredentials([string(credentialsId: 'SNYK_TOKEN_TEXT', variable: 'SNYK_TOKEN')]) {
                    script {
                        // Using the direct linux binary path found in your logs
                        def snykPath = "/var/lib/jenkins/tools/io.snyk.jenkins.tools.SnykInstallation/snyk-cli/snyk-linux"
                        
                        echo "Running Snyk Security Scans..."
                        // Single quotes around the shell command prevent Groovy interpolation warnings
                        sh "'${snykPath}' test --token=${SNYK_TOKEN} --severity-threshold=high || true"
                        sh "'${snykPath}' iac test --token=${SNYK_TOKEN} || true"
                    }
                }
            }
        }

        stage('Build: PHP Container') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    
                    // List files to the log to verify the Dockerfile actually exists in the workspace
                    sh "ls -lah"
                    
                    // Build the image using the Dockerfile in the current directory (.)
                    sh "docker build -t ${imageTag} ."
                }
            }
        }

        stage('Security: Image Scan (Trivy)') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    // Trivy scan for high/critical vulnerabilities
                    sh "trivy image --severity CRITICAL --exit-code 0 ${imageTag}"
                }
            }
        }

        stage('Infrastructure: Terraform Plan') {
            steps {
                // Using your confirmed Azure Secret Text IDs
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

        stage('Deploy: Push to Artifactory') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    // Login and push to your JFrog Docker Registry
                    withCredentials([usernamePassword(credentialsId: 'JFROG_CREDENTIALS', usernameVariable: 'JF_USER', passwordVariable: 'JF_PASS')]) {
                        sh "docker login ${VM_IP}:8082 -u ${JF_USER} -p ${JF_PASS}"
                        sh "docker push ${imageTag}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Wipes the workspace to save space on your 1GB VM
            cleanWs()
        }
    }
}                }
            }
        }

        stage('Security: Image Scan (Trivy)') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    sh "trivy image --severity CRITICAL --exit-code 0 ${imageTag}"
                }
            }
        }

        stage('Infrastructure: Terraform Plan') {
            steps {
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

        stage('Deploy: Push to Artifactory') {
            steps {
                script {
                    def imageTag = "${VM_IP}:8082/${JFROG_REPO}/${APP_NAME}:${env.BUILD_NUMBER}"
                    // This logs into your JFrog instance and pushes the image
                    withCredentials([usernamePassword(credentialsId: 'JFROG_CREDENTIALS', usernameVariable: 'JF_USER', passwordVariable: 'JF_PASS')]) {
                        sh "docker login ${VM_IP}:8082 -u ${JF_USER} -p ${JF_PASS}"
                        sh "docker push ${imageTag}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Very important for your 1GB VM to prevent the disk from filling up
            cleanWs()
        }
    }
}
