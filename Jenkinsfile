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
                git branch: 'main',
                    url: 'https://github.com/YosraMamdouh/AI-logs-metrics-monitor-system.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('backend') {
                    sh '''
                        docker build \
                            -t aiops-backend:${BUILD_NUMBER} \
                            .
                    '''
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                dir('backend') {
                    sh '''
                        docker run --rm \
                            aiops-backend:${BUILD_NUMBER} \
                            python -m pytest tests/ -v
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry(
                        'https://index.docker.io/v1/',
                        "${DOCKER_CREDS_ID}"
                    ) {

                        sh """
                            docker tag \
                                aiops-backend:${BUILD_NUMBER} \
                                ${DOCKER_IMAGE}:${BUILD_NUMBER}

                            docker tag \
                                aiops-backend:${BUILD_NUMBER} \
                                ${DOCKER_IMAGE}:latest
                        """

                        def appImage = docker.image(
                            "${DOCKER_IMAGE}:${BUILD_NUMBER}"
                        )

                        appImage.push()
                        appImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl create namespace ${K8S_NAMESPACE} \
                        --dry-run=client \
                        -o yaml | kubectl apply -f -

                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" \
                        K8s_YAML/05-backend-deployment.yaml

                    kubectl apply -f K8s_YAML/ \
                        -n ${K8S_NAMESPACE}
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    kubectl rollout status \
                        deployment/backend-deployment \
                        -n ${K8S_NAMESPACE} \
                        --timeout=60s
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