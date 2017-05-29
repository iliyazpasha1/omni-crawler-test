from urlparse import urljoin, urlparse

import re
from scrapy import Request
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders.crawl import CrawlSpider
#from scrapylib.processors import default_input_processor, default_output_processor
import scrapy
import json

__author__ = 'ttomlins'


class NormalizedJoin(object):
    """ Strips non-empty values and joins them with the given separator. """

    def __init__(self, separator=u' ', return_list=False):
        self.separator = separator
        self.return_list = return_list

    def __call__(self, values):
        result = self.separator.join(
            [value.strip() for value in values if value and not value.isspace()])
        if self.return_list:
            return [result]
        else:
            return result


class JobItem(Item):
    # required fields
    title = Field()
    # a unique id for the job on the crawled site.
    job_id = Field()
    # the url the job was crawled from
    url = Field()
    # name of the company where the job is.
    company = Field()

    # location of the job.
    # should ideally include city, state and country.
    # postal code if available.
    # does not need to include street information
    location = Field()
    description = Field()

    # the url users should be sent to for viewing the job. Sometimes
    # the "url" field requires a cookie to be set and this "apply_url" field will be differnt
    # since it requires no cookie or session state.
    apply_url = Field()

    # optional fields
    industry = Field()
    baseSalary = Field()
    benefits = Field()
    requirements = Field()
    skills = Field()
    work_hours = Field()


class JobItemLoader(ItemLoader):
    default_item_class = JobItem
    #default_input_processor = default_input_processor
    #default_output_processor = default_output_processor
    # all text fields are joined.
    description_in = Identity()
    description_out = NormalizedJoin()
    requirements_in = Identity()
    requirements_out = NormalizedJoin()
    skills_in = Identity()
    skills_out = NormalizedJoin()
    benefits_in = Identity()
    benefits_out = NormalizedJoin()


REF_REGEX = re.compile(r'\/(\d+)$')

APPEND_GB = lambda x: x.strip() + ", GB"


class SimplyLawJobs(CrawlSpider):

	start_urls = ["http://www.simplylawjobs.com/jobs"]
	name = 'lawjobsspider'
	fixed_urls = "http://www.simplylawjobs.com"
	
	def parse(self, response):
		#collect all job urls
		links = response.xpath('//a[@class="button radius view_job_btn"]/@href').extract()
		for link in links:
			#add fixed url with links extracted
			absolute_url = self.fixed_urls + link
			#call job_data method on each url
			yield scrapy.Request(absolute_url, callback=self.job_data)

    #----------------#
    #----------------#
    #-YOUR CODE HERE-#
    #----------------#
    #----------------#
	
	
	def job_data(self, response):
		#create instane of calls JobItem
		item = JobItem()
		#grab data from response page
		j= json.loads(response.xpath('//div[@class="columns small-12 medium-4 large-4 details"]/script/text()').extract()[0], strict=False)
		
		#crawl title of the job
		item['title'] = j.get('title')
		
		#crawl url of the job
		item['url'] = response.url
		
		#crawl company name 
		item['company'] = j['hiringOrganization']['name']
 		
		#crawl full address 
		item['location'] = j['jobLocation']['address']['addressLocality']
		
		#crawl description
		item['description'] = j.get('description')
		
		#apply_url requires authentication to crawl
		
		# optional fields
		item['industry'] = j.get('industry')
		#crawl salary
		item['baseSalary'] = j.get('baseSalary')
		
		return item


