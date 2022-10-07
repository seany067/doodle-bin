#[macro_use] extern crate rocket;
use rocket::fs::FileServer;
use rocket_dyn_templates::Template;
use std::collections::HashMap;
use rocket::serde::uuid::Uuid;

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

#[launch]
fn rocket() -> _ {
    rocket::build().attach(Template::fairing()).mount("/", routes![index, load]).mount("/static", FileServer::from("static/"))
}
