pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'mariamas32/aiops-backend'
        DOCKER_CREDS_ID = 'docker-registry-creds'
        K8S_NAMESPACE = 'aiops'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/zeyadmvtr/AI-logs-metrics-monitor-system.git'
            }
        }

        stage('Run Unit Tests') {
            steps {
                dir('backend') {
                    sh '''
                        # تم إزالة || echo للسماح للـ Pipeline باكتشاف الأخطاء الحقيقية
                        docker run --rm -v $(pwd):/app -w /app python:3.11-slim sh -c "pip install --no-cache-dir -r requirements.txt && pytest tests/"
                    '''
                }
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                dir('backend') {
                    script {
                        docker.withRegistry('https://index.docker.io/v1/', "${env.DOCKER_CREDS_ID}") {
                            def appImage = docker.build("${env.DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                            appImage.push()
                            appImage.push('latest')
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" K8s_YAML/05-backend-deployment.yaml
                    kubectl apply -f K8s_YAML/ -n ${K8S_NAMESPACE}
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl rollout status deployment/backend-deployment -n ${K8S_NAMESPACE} --timeout=60s
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
