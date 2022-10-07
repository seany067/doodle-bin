#[macro_use] extern crate rocket;
use rocket::fs::FileServer;
use rocket_dyn_templates::Template;
use std::collections::HashMap;
use rocket::serde::{Serialize, Desialize, json::Json, uuid::Uuid};

#[derive(Serialize)]
#[serde(crate = "rocket::serde")]
struct IdData {
    id: Uuid
}

#[derive(Serialize)]
#[derive(Desialize)]
#[serde(crate = "rocket::serde")]
struct DrawingData {

}

#[get("/")]
fn index() -> Template {
    let mut context = HashMap::new();
    context.insert("foo", "Hello, world!");
    return Template::render("index", context);
}

#[get("/<id>")]
fn load(id: Uuid) -> Template {
    let mut context = HashMap::new();
    context.insert("foo", "Hello, world!");
    println!("{}", id);
    return Template::render("index", context);
}

#[post("/", data = "<data>")]
fn save(data: Json<DrawingData>) -> Json<IdData> {
    let entryId = Uuid::new_v4()
    return Json(IdData {id: entryId});
}

#[post("/<id>", data = "<data>")]
fn save(id: Uuid, data: Json<DrawingData>) -> Json<IdData> {
    return Json(IdData {id:id});
}

#[launch]
fn rocket() -> _ {
    rocket::build().attach(Template::fairing()).mount("/", routes![index, load, save]).mount("/static", FileServer::from("static/"))
}
