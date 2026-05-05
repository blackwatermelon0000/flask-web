pipeline {
    agent any

    environment {
        APP_PORT   = '5000'
        DOCKER_IMG = 'student-app-test'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Pulling code from GitHub ==='
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '=== Building Docker image ==='
                sh 'docker build -t ${DOCKER_IMG} .'
            }
        }

        stage('Start Application') {
            steps {
                echo '=== Starting Flask application ==='
                sh '''
                    docker rm -f student-app 2>/dev/null || true
                    docker run -d \
                        --name student-app \
                        -p ${APP_PORT}:5000 \
                        ${DOCKER_IMG} \
                        python app.py
                    echo "Waiting for app to start..."
                    sleep 8
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '=== Running 15 Selenium test cases ==='
                sh '''
                    mkdir -p test-results
                    docker run --rm \
                        --name selenium-tests \
                        --network host \
                        -e BASE_URL=http://localhost:${APP_PORT} \
                        -v $(pwd)/test-results:/app/test-results \
                        ${DOCKER_IMG} \
                        python -m pytest tests/test_student_app.py \
                            -v \
                            --junit-xml=/app/test-results/results.xml \
                            2>&1 | tee test-results/test-output.log
                '''
            }
            post {
                always {
                    junit 'test-results/results.xml'
                }
            }
        }

        stage('Cleanup') {
            steps {
                echo '=== Cleaning up containers ==='
                sh '''
                    docker rm -f student-app 2>/dev/null || true
                    docker rmi ${DOCKER_IMG} 2>/dev/null || true
                '''
            }
        }
    }

    post {
        success {
            echo 'All tests passed.'
            emailext(
                subject: "BUILD SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    Build: ${env.BUILD_NUMBER}
                    Status: SUCCESS
                    All Selenium tests passed.
                    URL: ${env.BUILD_URL}
                """,
                to: 'your-email@gmail.com'
            )
        }
        failure {
            echo 'Build or tests failed.'
            emailext(
                subject: "BUILD FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    Build: ${env.BUILD_NUMBER}
                    Status: FAILED
                    Check logs: ${env.BUILD_URL}
                """,
                to: 'your-email@gmail.com'
            )
        }
    }
}