
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /build
COPY scheduler/pom.xml ./
RUN mvn -q -e -DskipTests package || true
COPY scheduler/src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /build/target/scheduler-jar-with-dependencies.jar /app/scheduler.jar
CMD ["java", "-jar", "/app/scheduler.jar"]
