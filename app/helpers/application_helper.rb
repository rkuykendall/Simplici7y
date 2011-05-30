# Methods added to this helper will be available to all templates in the application.
module ApplicationHelper

  # tab_for('Kitties', hash_for_kitties_path)
  # tab_for('Puppies', hash_for_puppies_path)
  def tab_for(name, options={})
    condition = (name.downcase == controller.controller_name)
    link_to_unless(condition, name, options) do
      rss = name + link_to(image_tag('rss.png'), "#{controller.controller_name}.rss", :class => 'rss')
      content_tag(:span, rss)
    end
  end
  
  def format(text)
    if text != nil
      text = Sanitize.clean(text)
      BlueCloth::new(text).to_html
    end
  end
  
  def clean(text)
    if text != nil
      text = Sanitize.clean(text)
    end
  end
  
end
