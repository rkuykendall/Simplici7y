class CreateScreenshots < ActiveRecord::Migration
  def self.up
    create_table :screenshots do |t|
      t.integer :item_id
      t.string :file
      t.string :title

      t.timestamps
    end
  end

  def self.down
    drop_table :screenshots
  end
end
