resolvers += Resolver.url("olegych-repo", url("https://bitbucket.org/olegych/mvn/raw/default/ivy2/"))(Resolver.ivyStylePatterns)

addSbtPlugin("com.typesafe.sbt" % "sbt-scalariform" % "1.2.0")

libraryDependencies += "org.scalariform" %% "scalariform" % "0.1.6-SCASTIE"

addSbtPlugin("io.get-coursier" % "sbt-coursier" % "1.0.0-M15")

//addSbtPlugin("com.geirsson" % "sbt-scalafmt" % "0.2.6")

addSbtPlugin("ch.epfl.lamp" % "sbt-dotty" % "0.1.0-RC1")

scalacOptions ++= Seq("-deprecation", "-feature")
