package base

import com.olegych.scastie.PastesActor.Paste
import java.util.concurrent.atomic.AtomicLong
import com.olegych.scastie.PastesActor

/**
  */
object TemplatePastes {
  private val pasteIds = new AtomicLong(1L) {
    def next = incrementAndGet()
  }

  val default = nextPaste( """
/***
coursier.CoursierPlugin.projectSettings
scalaVersion := "2.12.1"
*/
object Main extends App {
  println("Hello World!")
}
                           """)

  val templates = {
    List(
      "typelevel(ish)" -> nextPaste( """
/***
coursier.CoursierPlugin.projectSettings
scalaVersion := "2.12.1"
addCompilerPlugin("org.spire-math" %% "kind-projector" % "0.9.3")
libraryDependencies ++= {
  val scalazVersion = "7.2.10"
  val fs2Version = "0.9.4"
  val shapelessVersion = "2.3.2"
  val monocleVersion = "1.4.0"
  val spireVersion = "0.13.0"
  Seq(
    "org.scalaz" %% "scalaz-core" % scalazVersion,
    "org.scalaz" %% "scalaz-concurrent" % scalazVersion,
    "org.scalaz" %% "scalaz-effect" % scalazVersion,
    "com.chuusai" %% "shapeless" % shapelessVersion,
    "com.github.julien-truffaut" %% "monocle-generic" % monocleVersion,
    "com.github.julien-truffaut" %% "monocle-law" % monocleVersion,
    "com.github.julien-truffaut" %% "monocle-macro" % monocleVersion,
    "org.spire-math" %% "spire" % spireVersion,
    "co.fs2" %% "fs2-core" % fs2Version,
    "co.fs2" %% "fs2-io" % fs2Version
  )
}
*/
import scalaz._, Scalaz._
import scalaz.effect._
import shapeless._
import spire.math._
import spire.implicits._
import spire.random._
import fs2.{io, text}
import fs2.Task
import monocle._
import monocle.syntax._
import monocle.std.string._
object Main extends SafeApp {
  override def runc = IO.putStrLn("Hello" |+|  " World!")
}
        """)
      ,
      "lightbend" -> nextPaste( """
/***
coursier.CoursierPlugin.projectSettings
scalaVersion := "2.12.1"
libraryDependencies ++= Seq("com.typesafe.play" %% "play" % "2.6.0-M3")
*/

object Main extends App {
  println(play.api.libs.json.Json.obj("hello" -> "world"))
}
                                """)
      ,
      "sbt 0.13" -> nextPaste( """
/***
coursier.CoursierPlugin.projectSettings
sbtPlugin := true
*/
import sbt._
import Keys._
object Build extends Plugin with App {
  override def projectSettings = Seq(name := "hello")
}
                          """)
      ,
      "scala 2.11" -> nextPaste( """
/***
coursier.CoursierPlugin.projectSettings
scalaVersion := "2.11.9"
*/
object Main extends App {
  println("Hello World!")
}
                          """)
      ,
      "dotty" -> nextPaste( """
/***
com.felixmulder.dotty.plugin.DottyPlugin.projectSettings
scalaVersion := "0.1.1-20170402-054a4f9-NIGHTLY"
*/
object Main extends App {
  println("Hello World!")
}
                          """)
    )
  }

  def nextPaste(x: String): PastesActor.Paste = Paste(pasteIds.next, Some(x), None, None, None)
}
