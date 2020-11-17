
# Python 3.8
# By: LawlietJH

from threading import Thread
import requests
import time

class SubdomainFinder:
	
	def __init__(self, subdomains_total=0, mtpd=15):
		
		self.subdomains_total = subdomains_total
		self.mtpd = mtpd	# Max time per domain
		
		self.count = 0
		self.urls = []
		self.out_of_time = []
		
		self.load_domains()
	
	def load_domains(self):
		
		self.file_ = open('subdomains.txt', 'r')
		self.content = self.file_.read().splitlines()
		if self.subdomains_total:
			self.content = self.content[:self.subdomains_total]
		self.subdomains_total = len(self.content)
	
	def progress_bar(self, pos, chunks, qty=25, c=('█',' ')):
		
		block = 100 / qty
		chunk = 100 / chunks
		
		percent  = chunk * pos
		progress = percent // block
		progress += 1 if percent % block > 0 else 0
		spaces   = qty - progress
		# ~ if pos == chunks: percent = 100
		bar = '{}% |{}{}|'.format(str(int(percent)).rjust(3),c[0]*int(progress), c[1]*int(spaces))
		
		return bar
	
	def search(self, part, t):
		
		for subdomain in part:
			
			if subdomain in self.ignoreds:
				self.count += 1
				continue
			
			url = f'http://{subdomain}.{self.domain}'
			
			self.count += 1
			
			bar = self.progress_bar(self.count, self.subdomains_total)
			
			str_  = '\r [+] Searching: '
			str_ += f'{self.count}/{self.subdomains_total} '
			str_ += bar
			str_ += ' - Subdomain: ' + subdomain + '\t\t'
			
			print(str_, end='')
			
			try:
				t_i = time.perf_counter()
				requests.get(url)
			except requests.ConnectionError:
				pass
			else:
				self.urls.append(url)
			
			lapsed = time.perf_counter()-t_i
			if lapsed > self.mtpd:
				self.out_of_time.append((subdomain, lapsed))
	
	def gen_bin_lvl(self, lvl=1, limit=3, verbose=False, v_lvl=1):
		l = []
		for r in range(2**limit-1):
			r+=1
			b = str(bin(r))[2:].zfill(limit)
			if verbose and v_lvl in [1,3]: print(b)
			if b[-lvl] == '1':
				l.append(r)
		if verbose and v_lvl in [2,3]: print(l)
		return l
	
	def perttier_time(self, t):
		
		t = round(t, 2)
		
		ss = 0
		mm = 0
		hh = 0
		
		if t > 60:
			
			ss = int(t)%60
			mm = int(t/60)
			
			if mm > 60:
				mm = int(mm)%60
				hh = int(mm/60)
				o = f'{hh}:{mm}:{ss}'
			else:
				o = f'{mm}:{ss}'
		else:
			o = f'{t}s'
		
		return o
	
	def save_domains(self):
		
		with open('Discovered Subdomains - '+self.domain+'.txt', 'w') as f:
			
			f.write('\n[+] Discovered Subdomain:\n')
			f.write('\n    [+] Time lapsed: ' + self.t_end_pretty + '\n')
			
			for url in self.urls:
				
				f.write('\n' + url)
			
			f.close()
	
	def init(self, domain, threads=12, ignoreds=[], verb=True, v_lvl=1):	 # 0 <= v_lvl <= 7
		
		self.domain = domain
		self.thrs = threads
		self.ignoreds = ignoreds
		
		if self.thrs > self.subdomains_total: self.thrs = self.subdomains_total
		
		self.t_init = time.perf_counter()
		
		
		if verb and v_lvl in self.gen_bin_lvl(1): 
			print('\n')
		
		for t in range(self.thrs):
			
			init = int(len(self.content)/self.thrs) *  t
			end  = int(len(self.content)/self.thrs) * (t+1)
			part = self.content[init:end]
			
			thr = Thread(target=self.search, args=(part,t+1,))
			exec(f't{t} = thr')
			exec(f't{t}.start()')
		
		if end < self.subdomains_total:
			part = self.content[end:]
			thr_ = Thread(target=self.search, args=(part,t+1,))
			thr_.start()
			thr_.join()
		
		for t in range(self.thrs): exec(f't{t}.join()')
		
		self.t_end = time.perf_counter() - self.t_init
		
		self.t_end_pretty = self.perttier_time(self.t_end)
		
		if verb and v_lvl in self.gen_bin_lvl(1): 
			print('\n\n    [+] Time lapsed: ' + self.t_end_pretty)
		
		if verb and v_lvl in self.gen_bin_lvl(2):
			print('\n')
			for url in self.urls:
				print(' [+] Discovered Subdomain: ' + url)
		
		if verb and v_lvl in self.gen_bin_lvl(3):
			print('\n\n [-] Out of time:')
			for domain, lapsed in self.out_of_time:
				print('\t    ' + domain + ' - lapsed: ' + str(lapsed))
		
		self.save_domains()
		
		self.count = 0
		self.urls = []
		self.out_of_time = []



if __name__ == '__main__':	# Ejemplos de uso
	
	subdf = SubdomainFinder()
	
	subdf.init('amazon.com')
	
	ignoreds = ['mail', 'support', 'stash']
	
	subdf.init('netflix.com', threads=16, ignoreds=ignoreds)


