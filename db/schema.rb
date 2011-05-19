# This file is auto-generated from the current state of the database. Instead of editing this file, 
# please use the migrations feature of Active Record to incrementally modify your database, and
# then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your database schema. If you need
# to create the application database on another system, you should be using db:schema:load, not running
# all the migrations from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended to check this file into your version control system.

ActiveRecord::Schema.define(:version => 20080731230505) do

  create_table "downloads", :force => true do |t|
    t.integer  "user_id",    :limit => 11
    t.integer  "version_id", :limit => 11
    t.integer  "item_id",    :limit => 11
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "items", :force => true do |t|
    t.integer  "user_id",                :limit => 11
    t.integer  "tc_id",                  :limit => 11
    t.string   "name"
    t.text     "body"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "downloads_count",        :limit => 11, :default => 0,   :null => false
    t.integer  "reviews_count",          :limit => 11, :default => 0,   :null => false
    t.string   "permalink"
    t.integer  "screenshots_count",      :limit => 11, :default => 0,   :null => false
    t.integer  "versions_count",         :limit => 11, :default => 0,   :null => false
    t.datetime "version_created_at"
    t.float    "ratings_count",                        :default => 0.0
    t.float    "ratings_weighted_count",               :default => 0.0
  end

  create_table "reviews", :force => true do |t|
    t.integer  "item_id",    :limit => 11
    t.integer  "version_id", :limit => 11
    t.integer  "user_id",    :limit => 11
    t.string   "title"
    t.text     "body"
    t.integer  "rating",     :limit => 11
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "relevancy",  :limit => 11, :default => 0, :null => false
  end

  create_table "screenshots", :force => true do |t|
    t.integer  "item_id",    :limit => 11
    t.string   "file"
    t.string   "title"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "taggings", :force => true do |t|
    t.integer "tag_id",        :limit => 11, :null => false
    t.integer "taggable_id",   :limit => 11, :null => false
    t.string  "taggable_type",               :null => false
  end

  add_index "taggings", ["tag_id", "taggable_id", "taggable_type"], :name => "index_taggings_on_tag_id_and_taggable_id_and_taggable_type", :unique => true

  create_table "tags", :force => true do |t|
    t.string "name",      :null => false
    t.string "permalink"
  end

  add_index "tags", ["name"], :name => "index_tags_on_name", :unique => true

  create_table "users", :force => true do |t|
    t.string   "login"
    t.string   "email"
    t.string   "crypted_password",          :limit => 40
    t.string   "salt",                      :limit => 40
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "remember_token"
    t.datetime "remember_token_expires_at"
    t.string   "permalink"
    t.integer  "admin",                     :limit => 11, :default => 0, :null => false
  end

  create_table "versions", :force => true do |t|
    t.integer  "item_id",         :limit => 11
    t.string   "name"
    t.string   "file"
    t.text     "body"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "downloads_count", :limit => 11, :default => 0, :null => false
  end

end
